import os
from pathlib import Path
import glob
import logging
import re

from django.core.management.base import BaseCommand
from rapid.models import DocumentGroup
from django.core.files.base import ContentFile
from rapid.views import COUNTIES
logger = logging.getLogger(__name__)

#/home/theo/git/rapid/media/X/general GWmaps

def key(val, d):
    for k,v in d.items():
        if v == val:
            return k
    raise StopIteration

class Command(BaseCommand):

    help = 'Register manually uploaded documents'
    
    def add_arguments(self, parser):
        parser.add_argument('-c','--county',default='0',help='county')
        parser.add_argument('-g','--group',help='group')
        parser.add_argument('pattern',help='pattern')
        
    def handle(self, *args, **options):
        county_id = options.get('county')
        group_id = options['group']
        pattern = options['pattern']
        try:
            group = DocumentGroup.objects.get(pk=group_id)
        except:
            group = DocumentGroup.objects.get(name__istartswith=group_id)
        if county_id != '0':
            if county_id in ['12345']:
                county_name = COUNTIES[county_id]
            else:
                county_name = county_id.title()
                county_id = key(county_name, COUNTIES)
            if group.name != county_name:
                # add sub group for county
                group, created = group.children.get_or_create(name=county_name)
                if created:
                    logger.debug(f'Added group {group}')
        for filename in glob.glob(pattern):
            logger.debug(filename)
            name = Path(filename).stem
            # remove 'ISL - '
            pattern = r'^[A-Z]{3}\s?[-_]\s?'
            name = re.sub(pattern, '', name)
            with open(filename,'rb') as f:
                content = f.read()
                doc_file = ContentFile(content,os.path.basename(filename))
            doc, created = group.document_set.get_or_create(name=name,defaults = {
                'cluster': county_id,
                'description': name,
                'url': '',
                'doc': doc_file
                })
            if created:
                logger.debug(f'Created document {doc}')
