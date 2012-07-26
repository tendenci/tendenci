from tendenci.core.registry import site
from tendenci.core.registry.base import PluginRegistry, lazy_reverse
from tendenci.apps.projects.models import Project


class ProjectRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create projects type of content'

site.register(Project, ProjectRegistry)
