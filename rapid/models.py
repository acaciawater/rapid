'''
Created on May 20, 2019

@author: theo
'''
import os
import json

from django.contrib.auth.models import User
from django.db import models
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _

from ogc.models import Layer as OCGLayer

import logging
from django.db.utils import IntegrityError
from django.conf import settings
logger = logging.getLogger(__name__)


class Map(models.Model):
    ''' Collection of map layers '''
    name = models.CharField(_('name'), max_length=100)
    bbox = models.CharField(_('extent'), max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def clone(self, user):
        ''' clone this map for a specific user '''
        usermap = Map.objects.filter(name=self.name, user=user).first()
        if usermap:
            raise IntegrityError('Map already exists.')
        
        # query groups and evaluate queryset
        groups = list(self.group_set.all())

        # clone ourselves
        usermap = self
        usermap.pk = None
        usermap.user = user
        usermap.save()

        # clone groups and layers
        for group in groups:
            # query layers and evaluate queryset
            layers = list(group.layer_set.all())
            group.pk = None
            group.map = usermap
            group.save()
            for layer in layers:
                layer.pk = None
                layer.map = usermap
                layer.group = group
                layer.save()
    
        return usermap

    def to_json(self):
        ''' return json dict of groups with layers on the map. '''
        def layers(group):
            return [{'id': layer.id, 
                     'index': index,
                     'layer_id': layer.layer.id,
                     'name': layer.layer.title,
                     'url': layer.layer.server.url,
                     'downloadable': layer.allow_download,
                     'clickable': layer.clickable,
#                      'stylesheet': layer.stylesheet,
                     'visible': layer.visible,
                     'legend': layer.layer.legend_url(),
                     'options': layer.options()
                     } 
                    for index, layer in enumerate(group.layer_set.order_by('order'))]

        return json.dumps({
            'groups': [
                    {'name': group.name, 
                     'layers': layers(group),
                     'state': 'show' if group.open else 'hide',
                    } for group in self.group_set.order_by('order')
                ]
            })
    
    def get_extent(self):
        ''' compute and return map extent from layers '''
        map_extent = []
        for layer in self.layer_set.exclude(use_extent=False):
            bbox = layer.extent()
            if bbox:
                if map_extent:
                    map_extent[0] = min(bbox[0], map_extent[0])
                    map_extent[1] = min(bbox[1], map_extent[1])
                    map_extent[2] = max(bbox[2], map_extent[2])
                    map_extent[3] = max(bbox[3], map_extent[3])
                else:
                    map_extent = list(bbox)
        return map_extent

    def set_extent(self):
        ''' update self.bbox with string representation of current extent '''
        ext = self.get_extent()
        self.bbox = ','.join(map(str, ext))
        self.save(update_fields=('bbox',))
        return ext

    def extent(self):
        ''' return current extent. Calculate if self.bbox is undefined '''
        return list(map(float, self.bbox.split(','))) if self.bbox else self.set_extent()

    def __str__(self):
        result = self.name
        if self.user:
            result += ' ({})'.format(self.user)
        return result

    def get_absolute_url(self):
        return reverse('map-detail', args=[self.pk])


class Group(models.Model):
    ''' Layer group '''
    name = models.CharField(_('group'), max_length=100)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    order = models.SmallIntegerField(_('order'), default=1)
    open = models.BooleanField(_('open'), default=False)
    
    def layer_count(self):
        return self.layer_set.count()

    def __str__(self):
        result = '{}:{}'.format(self.map.name, self.name)
        if self.map.user:
            result += ' ({})'.format(self.map.user)
        return result
    
    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        unique_together = ('name', 'map')


class Layer(models.Model):
    '''
    Layer on the map.
    Layer can be configured (by order, visibility, opacity etc)
    '''
    map = models.ForeignKey(Map, models.CASCADE, verbose_name=_('map'))
    layer = models.ForeignKey(OCGLayer, models.CASCADE, null=True)
    group = models.ForeignKey(Group, models.SET_NULL,
                              blank=True, null=True, verbose_name=_('group'))
    order = models.SmallIntegerField(_('order'),default=1)
    visible = models.BooleanField(_('visible'), default=True)
    visible.boolean = True
    format = models.CharField(_('format'), max_length=50, default='image/png')
    minzoom = models.SmallIntegerField(_('minzoom'), null=True, blank=True)
    maxzoom = models.SmallIntegerField(_('maxzoom'), null=True, blank=True)
    transparent = models.BooleanField(_('transparent'), default=True)
    transparent.Boolean = True
    opacity = models.DecimalField(
        _('opacity'), max_digits=4, decimal_places=1, default=1.0)

    use_extent = models.BooleanField(
        default=True, verbose_name=_('Use extent'))
    clickable = models.BooleanField(default=False, verbose_name=_(
        'clickable'), help_text=_('show popup with info when layer is clicked'))
    clickable.boolean = True
    properties = models.CharField(_('properties'), max_length=200, null=True, blank=True,
                                  help_text=_(
                                      'comma separated list of properties to display when layer is clicked'))

    allow_download = models.BooleanField(default=False, verbose_name=_(
        'downloadable'), help_text=_('user can download this layer'))
    allow_download.Boolean = True
    stylesheet = models.URLField(_('stylesheet'), null=True, blank=True, help_text=_(
        'url of stylesheet for GetFeatureInfo response'))

    def extent(self):
        ''' return extent of WMS layer in WGS84 coordinates '''
        return self.layer.extent()

    def options(self):
        '''
        returns options dict for Leaflet overlays
        '''
        ret = {
            'service': self.layer.server.service_type,
            'version': self.layer.server.version,
            'layers': self.layer.layername,
            'format': self.format,
            'transparent': self.transparent,
            'opacity': float(self.opacity),
        }
        if self.properties:
            ret['propertyName'] = self.properties
        if self.layer.server.service_type == 'WMS':
            if self.minzoom:
                ret['minZoom'] = self.minzoom
            if self.maxzoom:
                ret['maxZoom'] = self.maxzoom
            if self.layer.tiled:
                ret['tiled'] = True
        return ret

    def __str__(self):
        return '{}'.format(self.layer)


class DocumentGroup(models.Model):
    name = models.CharField(max_length=100)    
    parent = models.ForeignKey('DocumentGroup', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    open = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)
    
    def docs(self,cluster=0):
        ''' returns complete list of documents of this group and its children '''
        query = self.document_set.all()
        if cluster:
            query = query.filter(cluster=cluster)  
        for doc in query:
            yield doc
        for child in self.children.all():
            yield from child.docs(cluster)
        
    def empty(self,cluster=0):
        ''' returns true if there are no documents in this group, or any of its children ''' 
        try:
            next(self.docs(cluster))
            return False
        except StopIteration:
            return True
    
    def __str__(self):
        if self.parent is not None:
            # insert parent name
            return f'{self.parent}-{self.name}'
        else:
            return self.name


def upload_to_cluster(instance, filename):
    return 'cluster{0}/{1}'.format(instance.cluster or 0, filename)
    
class Document(models.Model):
    ''' Downloadable document '''

    from preview_generator.manager import PreviewManager
    preview_manager = PreviewManager(os.path.join(settings.MEDIA_ROOT,'preview'), create_folder=True)

    group = models.ForeignKey(DocumentGroup,on_delete=models.CASCADE)
    cluster = models.CharField(max_length=30,blank=True,null=True)
    name = models.CharField(max_length=100)    
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True,null=True)
    doc = models.FileField(upload_to=upload_to_cluster, blank=True, null=True)
    preview = models.ImageField(upload_to='preview', blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=1)
    
    def __str__(self):
        return self.name

    def create_preview(self, height=1080):
        try:
            path = self.preview_manager.get_jpeg_preview(self.doc.path, height=height)
            index = path.find('preview')
            name = path[index:]
        except:
            name = 'na.png'
        self.preview.name = name
        self.save()
            
    @property
    def preview_url(self):
        if not (self.preview and os.path.exists(self.preview.path)):
            self.create_preview()
        return self.preview.url if self.preview else None
    
    class Meta:
        ordering = ('name',)

