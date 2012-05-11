from registry import site
from registry.base import PluginRegistry, lazy_reverse
from S_P_LOW.models import S_S_CAP


class S_S_CAPRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create S_P_LOW type of content'

site.register(S_S_CAP, S_S_CAPRegistry)
