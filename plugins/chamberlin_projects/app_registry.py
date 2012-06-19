from registry import site
from registry.base import PluginRegistry, lazy_reverse
from chamberlin_projects.models import Project


class ProjectRegistry(PluginRegistry):
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
