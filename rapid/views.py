'''
Created on May 15, 2019

@author: theo
'''
import json

from django.conf import settings
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseNotFound,\
    JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .models import Map, DocumentGroup, Layer
from sorl.thumbnail.shortcuts import get_thumbnail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


# class MapDetailView(LoginRequiredMixin, DetailView):
class MapDetailView(DetailView):
    ''' View with leaflet map, legend and layer list '''
    model = Map

    def get_map(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['api_key'] = settings.GOOGLE_MAPS_API_KEY
        context['options'] = {'zoom': 12, 'center': [52, 5], 'minZoom': 4}
        map_object = self.get_map()
        context['map'] = map_object
        context['extent'] = map_object.extent()
        return context


@csrf_exempt
#@login_required
def reorder(request, pk):
    ''' reorder layers in map
        request.body contains ids of layers as json array in proper order
    '''
    if not request.user.is_authenticated:
        return HttpResponse('Authentication required to persist order of layers.', status=401)
 
    usermap = get_object_or_404(Map, pk=pk, user=request.user) # add user to query to make user user owns the map
    layer_ids = json.loads(request.body.decode('utf-8'))
    for index, layid in enumerate(layer_ids):
        try:
            layer = usermap.layer_set.get(pk=layid) 
        except Layer.DoesNotExist:
            return HttpResponseNotFound('Layer with id={} not found in map {}'.format(layid, usermap))
        if layer.order != index:
            layer.order = index
            layer.save(update_fields=('order',))

    return HttpResponse(status=200)

@csrf_exempt
# @login_required
def toggle(request, mapid, layid):
    '''
        Toggle visibility of a layer
    '''
    
    if not request.user.is_authenticated:
        return HttpResponse('Authentication required to persist visibility of layers.', status=401)
    
    layer = get_object_or_404(Layer, pk=layid)
    layer.visible = not layer.visible
    layer.save(update_fields=('visible',))
    return HttpResponse(status=200)
    
class HomeView(TemplateView):
    template_name = 'home.html'

# class BrowseView(LoginRequiredMixin, TemplateView):
class BrowseView(TemplateView):
    template_name = 'browse.html'
    
class OverlayView(TemplateView):
    template_name = 'overlay.html'


CLUSTERS = {
    '0': 'Ethiopia', # only for admins?
    '1': 'Wag Himra',
    '2': 'Afar',
    '3': 'Siti',
    '4': 'Liben',
    '5': 'Bale',
    '6': 'Borena',
    '7': 'Wolayta',
    '8': 'South Omo'
}


def map_proxy(request):
    ''' resolve map id from cluster name or number '''
    cluster = request.GET.get('cluster')
    if not cluster:
        return HttpResponseNotFound('Cluster name or number is missing.')
    clustername = CLUSTERS[cluster] if cluster in '012345678' else cluster
    
    map_query = Map.objects.filter(name__icontains=clustername)
    if request.user is None or request.user.is_anonymous:
        clustermap = map_query.filter(user__isnull=True).first()
    else:
        clustermap = map_query.filter(user=request.user).first()
    if clustermap is None:
        # try to clone a default map
        defmap = Map.objects.filter(name__icontains=clustername,user__isnull=True).first()
        if not defmap:
            return HttpResponseNotFound(f'Map {clustername} not found for user {request.user}')
        clustermap = defmap.clone(request.user)
    return redirect('map-detail', pk=clustermap.pk)


# @login_required
def get_map(request, pk):
    ''' return user's layer configuration for all groups in the map '''
    map_obj = get_object_or_404(Map, pk=pk)
    return HttpResponse(map_obj.to_json(), content_type='application/json')

# @login_required
def docs2json(request):
    ''' return json response with all documents grouped by theme '''
    
    from maps.engine import engine
    
    def process_group(cluster, group, result):
        data = {
            'id': group.id,
            'name': group.name,
            'state': 'open' if group.open else 'closed',
            'documents': process_docs(cluster, group),
            'folders': []
        }
        result.append(data)
        for child in group.children.order_by('order'):
            if not child.empty(cluster):
                process_group(cluster, child, data['folders'])

    def process_docs(cluster, group):
        result = []
        queryset = group.document_set.order_by('cluster','order','name')
        if cluster:
            queryset = queryset.filter(Q(cluster=cluster)|Q(cluster=0))
        for doc in queryset:
            item = {
                'id': doc.id,
                'name': doc.name,
                'description': doc.description,
                }
            if doc.doc:
                item['url'] = doc.url or doc.doc.url
                try:
                    with engine(doc.doc.name):
                        img = get_thumbnail(doc.doc, 'x600')
                        if img:
                            item['img'] = img.url
                except ValueError:
                    pass
            result.append(item)
        return result
    
    root = DocumentGroup.objects.get(parent__isnull=True)
    cluster = request.GET.get('cluster',0)
    try:
        cluster = int(cluster)
    except ValueError:
        cluster = 0
    result = []
    process_group(cluster, root, result)
    return JsonResponse({'results': result})

