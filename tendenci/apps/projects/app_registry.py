from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.projects.models import Project


class ProjectRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create projects type of content'

site.register(Project, ProjectRegistry)
