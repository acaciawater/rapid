import re
from django.contrib.admin import default_app_config
from sorl.thumbnail.engines import convert_engine 
default_app_config = 'rapid.apps.RapidConfig'

# Change size regex for identify in convert_engine 
# Version: ImageMagick 6.9.7-4 Q16 x86_64 20170114 http://www.imagemagick.org
convert_engine.size_re = re.compile(r'^(?:\S+)\s(?:\S+)\s(?P<x>\d+)x(?P<y>\d+)')
