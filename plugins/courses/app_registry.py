from registry import site
from registry.base import PluginRegistry, lazy_reverse
from courses.models import Course


class CourseRegistry(PluginRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create courses type of content'
    
    url = {
        'add': lazy_reverse('courses.add'),
        'search': lazy_reverse('courses.search'),
    }

site.register(Course, CourseRegistry)
