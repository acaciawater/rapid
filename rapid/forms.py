'''
Created on Aug 29, 2019

@author: theo
'''

from django import forms
from .models import Map


class LayerPropertiesForm(forms.Form):
    ''' Form to change layer properties in admin page '''
    visible = forms.NullBooleanField(required=False)
    use_extent = forms.NullBooleanField(required=False)
    clickable = forms.NullBooleanField(required=False)
    transparent = forms.NullBooleanField(required=False)
    opacity = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    allow_download = forms.NullBooleanField(required=False)
    order = forms.IntegerField(required=False)


class SelectMapForm(forms.Form):
    ''' Form to select a map in admin page '''
    map = forms.ModelChoiceField(queryset=Map.objects.all(), required=False)
