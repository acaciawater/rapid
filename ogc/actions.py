import json

from django.contrib import messages
from owslib.feature.schema import get_schema

import geopandas as gpd
import re


def classify(modeladmin, request, queryset):
    ''' create default legend classification '''
    num_created = 0
    for legend in queryset:
        try:
            legend.create_default()
            num_created += 1
        except Exception as e:
            messages.error(request,e)
    messages.success(request, f'{num_created} legends created')
classify.short_description = 'Create default classifcation for selected legends'

def create_legends(modeladmin, request, queryset):
    ''' create default WFS legends for all properties in a layer'''
    num_created = 0
    wfs_layers = queryset.filter(server__service_type='WFS')
    for layer in wfs_layers:
        try:
            service = layer.server.service
            response = service.getfeature(typename=layer.layername,outputFormat='GeoJSON')
            data = json.loads(response.read())
            
            # geopandas does not like points without (complete) coordinates
            def has_coords(feature):
                geom = feature.get('geometry')
                if geom:
                    coords = geom.get('coordinates')
                    if coords:
                        return isinstance(coords,list) and len(coords)>1 and all(coords)
                return False
            data['features'] = filter(has_coords, data['features'])
            
            features = gpd.GeoDataFrame.from_features(data)
            exclude = ['geometry','fid','ogc_fid','no','nr','id','sn', 'x','y','adindanx','adindany','remarks','remark','lon','lat','longitude','latitude','easting','northing']
            for name, series in features.iteritems():
                if name.lower() not in exclude:
                    legend, _created = layer.legends.get_or_create(title=name, property=name)
                    try:
                        legend.create_default(series)
                    except Exception as e:
                        messages.error(request, e)
                    num_created += 1
        except Exception as e:
            messages.error(request, e)
    messages.success(request, f'{num_created} legends created')
    
create_legends.short_description = 'Create default legends'
