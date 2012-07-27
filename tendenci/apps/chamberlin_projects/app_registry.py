from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.chamberlin_projects.models import Project


class ProjectRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create Projects type of content'

    url = {
        'search': lazy_reverse('chamberlin_projects.search'),
        'list': lazy_reverse('chamberlin_projects'),
        'add': lazy_reverse('admin:chamberlin_projects_project_add'),
    }

site.register(Project, ProjectRegistry)
