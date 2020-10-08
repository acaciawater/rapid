'''
support context switching of thumbnail engines. default = PIL
but hat does not work with PDF thumbnails.
Imagemagick works for PDF, but is very slow
'''

from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail import default
from contextlib import contextmanager

PDF_ENGINE='sorl.thumbnail.engines.convert_engine.Engine'
PIL_ENGINE='sorl.thumbnail.engines.pil_engine.Engine'

pil = get_module_class(PIL_ENGINE)()
pdf = get_module_class(PDF_ENGINE)()

@contextmanager
def engine(docname):
    ''' select appropriate thumbnail engine. Use Imagemagick for PDF, else use Pillow '''
    doc_engine = pdf if docname.lower().endswith('.pdf') else pil
    old_engine = default.engine 
    default.engine = doc_engine
    yield doc_engine
    default.engine = old_engine
