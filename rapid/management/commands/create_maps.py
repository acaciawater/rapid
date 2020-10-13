import logging

from django.core.management.base import BaseCommand
from ogc.models.server import Server
from django.shortcuts import get_object_or_404
from rapid.models import Map

logger = logging.getLogger(__name__)

def key(val, d):
    for k,v in d.items():
        if v == val:
            return k
    raise StopIteration

class Command(BaseCommand):

    help = 'Register manually uploaded documents'
    
    def add_arguments(self, parser):
        parser.add_argument('-c','--county',default='0',help='county')

    def handle(self, *args, **options):
        server = get_object_or_404(Server, name='Atlas')
        m = get_object_or_404(Map, name='Kenya Rapid')
        g,_ = m.group_set.get_or_create(name='Layers')
        for index, layer in enumerate(server.layer_set.all()):
            m.layer_set.update_or_create(layer=layer, defaults = {
                'group': g,
                'order': index,
                'visible': False,
                'allow_download': True,
                })
