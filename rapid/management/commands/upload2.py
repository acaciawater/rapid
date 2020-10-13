import os
from pathlib import Path
import logging
import re

from django.core.management.base import BaseCommand
from rapid.models import DocumentGroup
from django.core.files.base import ContentFile
from rapid.views import COUNTIES
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
        parser.add_argument('-g','--group',help='group')
        parser.add_argument('-r','--recursive',action='store_true',help='traverse folders recursively')
        parser.add_argument('-p','--pattern',default='',help='regex search pattern')
        parser.add_argument('folder',help='folder')

    def add_files(self, group, folder, county, recursive, pattern):

        for root, dirs, files in os.walk(folder):

            tail = root[len(folder)+1:]

            # create subgroups if needed
            target = group
            for name in tail.split('/'):
                if name:
                    name = name.title()
                    target, created = target.children.get_or_create(name=name)
                    if created:
                        logger.debug(f'Created group {target}')
            
            for filename in files:
                if pattern and not pattern.search(filename):
                    logger.debug(f'Skipped {filename}')
                    continue

                path = Path(root)/filename
                logger.debug(path)

                # remove 'ISL - '
                name = re.sub(r'^[A-Z]{3}\s?[-_]\s?', '', path.stem)
                with open(path,'rb') as f:
                    content = f.read()
                    doc_file = ContentFile(content,path.name)
                doc, created = target.document_set.get_or_create(name=name,defaults = {
                    'cluster': county,
                    'description': name,
                    'url': '',
                    'doc': doc_file
                    })
                if created:
                    logger.debug(f'Created document {doc}')
        

    def handle(self, *args, **options):
        county = options.get('county')
        group_id = options['group']
        folder = options['folder']
        pattern = options['pattern']
        recursive = options['recursive']
        
        if pattern:
            pattern = re.compile(pattern)
        try:
            group = DocumentGroup.objects.get(pk=group_id)
        except:
            group = DocumentGroup.objects.get(name__istartswith=group_id)
        if county != '0':
            if county in ['12345']:
                county_name = COUNTIES[county]
            else:
                county_name = county.title()
                county = key(county_name, COUNTIES)
            if group.name != county_name:
                # add sub group for county
                group, created = group.children.get_or_create(name=county_name)
                if created:
                    logger.debug(f'Added group {group}')
        
        self.add_files(group, folder, county, recursive, pattern)
        