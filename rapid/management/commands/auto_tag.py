import logging

from django.core.management.base import BaseCommand
from rapid.models import Document, DocumentGroup
from rapid.views import COUNTIES

logger = logging.getLogger(__name__)

def tag(groups, cluster, force=False, recurse=True):
    ''' tag all documents in a group '''
    for group in groups:
        logger.debug(f'Tagging group {group}')
        query = group.document_set.all()
        if not force:
            # take only docs without cluster
            query = query.filter(cluster=0)
#         query.update(cluster=cluster)
        if recurse:
            tag(group.children.all(), cluster, force, recurse)

def process_groups(groups, names, force=False, recurse=True):
    for group in groups:
        name = group.name.lower()
        tags = [k for k,v in names.items() if v in name]
        if len(tags) == 1:
            tag([group], tags[0], force, recurse)
        elif recurse:
            process_groups(group.children.all(), names, force, recurse)

def process_docs(names, force, recurse):
    query = Document.objects.all()
    if not force:
        query = query.filter(cluster=0)
    for doc in query:
        name = doc.name.lower()
        tags = [k for k,v in names.items() if v in name]
        if len(tags) == 1:
            logger.debug(f'Tagging document {doc.name}')
            doc.cluster = tags[0]
#                 doc.save()
    
class Command(BaseCommand):

    help = 'Tag documents from group or doc name'
    
    def add_arguments(self, parser):
        parser.add_argument('-f','--force',action='store_true',help='force')
        parser.add_argument('-r','--recurse',action='store_false',help='no recurse')

    def handle(self, *args, **options):
        force = options['force']
        recurse = options['recurse']
        names = {k:v.lower() for k,v in COUNTIES.items()}

        process_groups(DocumentGroup.objects.filter(parent__isnull=True), names, force=force, recurse=recurse)
        process_docs(names, force=force, recurse=recurse)
        
