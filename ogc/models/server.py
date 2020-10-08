from django.db import models
from django.utils.translation import gettext_lazy as _
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService

SERVICES = (
    ('WMS','WMS'),
    ('WFS','WFS')
)

VERSIONS = (
    ('WMS', (
        ('1.1.1','1.1.1'),
        ('1.3.0','1.3.0'),
        )
    ),
    ('WFS', (
        ('1.0.0','1.0.0'),
        ('1.1.0','1.1.0'),
        ('2.0.0','2.0.0'),
        ('3.0.0','3.0.0'),
        )
    )
)

class Server(models.Model):
    ''' OWS server '''
    name = models.CharField(_('name'), max_length=100, unique=True)
    url = models.URLField(_('url'), max_length=255)
    service_type = models.CharField(_('type'), max_length=4, choices=SERVICES, default='WMS')
    version = models.CharField(_('version'), max_length=10, choices=VERSIONS, default='1.3.0')

    def __str__(self):
        return self.name

    @property
    def service(self):
        if self.service_type == 'WMS':
            return WebMapService(self.url, self.version)
        elif self.service_type == 'WFS':
            return WebFeatureService(self.url, self.version)
        else:
            raise ValueError('Service not supported')

    def layer_details(self, layername = None):
        if layername is None:
            # return details of all layers
            service = self.service
            return {layer: service[layer] for layer in service.contents}
        else:
            # single layer
            return {layername: self.service[layername]}
    
    def enum_layers(self):
        for layer in self.service.contents:
            yield layer

    def update_layers(self, delete_nonexisting=True):

        if delete_nonexisting:
            # delete layers that are not reported in service contents
            newLayers = set(self.enum_layers())
            self.layer_set.exclude(layername__in=newLayers).delete()

        # create new layers
        numCreated = 0
        for layername, details in self.layer_details().items():
            _layer, created = self.layer_set.get_or_create(layername=layername,defaults = {
                'title': details.title or layername,
                'attribution': details.attribution.get('title','') if hasattr(details,'attribution') else ''
            })
            if created:
                numCreated += 1
        return numCreated

        
    class Meta:
        verbose_name = _('Server')
        
