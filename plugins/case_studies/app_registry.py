from registry import site
from registry.base import PluginRegistry, lazy_reverse
from models import CaseStudy


class CaseStudyRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create case studies of clients'

site.register(CaseStudy, CaseStudyRegistry)
