from django.db import models
from django.utils.translation import gettext_lazy as _
from colorsys import hsv_to_rgb
from ogc.models.layer import Layer
import json
import pandas as pd

def hsv2hex(h,s=1,v=1):
    h = 0.6667 * (1.0 - h) # reverse colors and clip at 245 degrees (blue)
    r,g,b = map(lambda c: int(c*255), hsv_to_rgb(h,s,v))
    return '#%02x%02x%02x' % (r,g,b)
    

class Legend(models.Model):
    ''' provide a legend for a property on a WFS layer '''
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE, related_name='legends', limit_choices_to={'server__service_type': 'WFS'})
    property = models.CharField(_('property'), max_length=40)
    title = models.CharField(_('title'),max_length=40,default=_('legend'))

    def __str__(self):
        return '%s.%s.%s' % (self.title, self.layer.layername, self.property)

    def lookup(self, value):
        if hasattr(self, 'range_set'):
            for entry in self.range_set.all():
                if entry.hi > value:
                    return {self.property: {'low': entry.lo, 'high': entry.hi, 'color': entry.color, 'label': entry.label}}
        elif hasattr(self, 'value_set'):
            for entry in self.value_set.all():
                if entry.value == value:
                    return {self.property: {'value': value, 'color': entry.color, 'label': entry.label}}
        raise ValueError(f'No legend entry found for {self.property}={value}')

    def get_features(self):
        import geopandas as gpd
        service = self.layer.server.service
        response = service.getfeature(typename=self.layer.layername,propertyname=self.property,outputFormat='GeoJSON')
        data = json.loads(response.read())
        return gpd.GeoDataFrame.from_features(data)

    def dup(self, legend):
        ''' Duplicate class boundaries from another legend'''
        
        def clone(o):
            o.pk = None
            o.legend = self
            o.save()
             
        self.range_set.all().delete()
        for r in legend.range_set.all():
            clone(r)

        self.value_set.all().delete()
        for v in legend.value_set.all():
            clone(v)
            
        
    def create_default(self, series=None):
        
        quantiles = [0,0.25,0.5,0.75,1.0]
        colors = ['#0000ff','#09d609','#ffc800','#ff0000']

        ''' create a default legend '''
        if series is None:
            values = self.get_features()[self.property]
            series = values.dropna()
        else:
            series = series.dropna()

        if series.size > 1:
            from pandas.api.types import is_numeric_dtype
            if is_numeric_dtype(series):
                # use quartiles
                q = series.quantile(quantiles)
                limits = q.values
                lo = limits[0]
                limits = limits[1:]
                self.range_set.all().delete()
                for index, hi in enumerate(limits):
#                     color = hsv2hex(float(index) / float(len(limits)-1))
                    color = colors[index] 
                    self.range_set.create(lo=lo, hi=hi, color=color, label = '%g - %g' % (lo,hi))
                    lo = hi
            else:
                series = series.unique()
                if series.size > 1:
                    if series.size > 24:
                        raise ValueError(f'{self.layer}:{self.property} is not numeric and has too many unique values to classify')
                    self.value_set.all().delete()
                    for index, value in enumerate(series):
                        if not pd.isnull(value):
                            color = hsv2hex(float(index) / float(series.size-1))
                            self.value_set.create(value=value[:40], color = color, label = str(value))
 

class Entry(models.Model):
    legend = models.ForeignKey(Legend,on_delete=models.CASCADE)
    color = models.CharField(max_length=20)    
    label = models.CharField(max_length=80,null=True,blank=True)

    class Meta:
        abstract = True
        
class Range(Entry):
    lo = models.FloatField()
    hi = models.FloatField()
    
    class Meta:
        ordering = ('lo','hi')
        
class Value(Entry):
    value = models.CharField(max_length=40)
    class Meta:
        ordering = ('value',)
            