from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry
from tendenci.apps.projects.models import Project


class ProjectRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Create projects type of content'

site.register(Project, ProjectRegistry)
