from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse
from tendenci.apps.studygroups.models import StudyGroup


class StudyGroupRegistry(AppRegistry):
    version = '1.0'
    author = 'Tendenci - The Open Source AMS for Associations'
    author_email = 'programmers@tendenci.com'
    description = 'Create studygroups type of content'

    url = {
        'add': lazy_reverse('studygroups.add'),
        'search': lazy_reverse('studygroups.search'),
    }

site.register(StudyGroup, StudyGroupRegistry)
