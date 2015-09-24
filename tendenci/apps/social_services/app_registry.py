from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import AppRegistry, lazy_reverse

from tendenci.apps.social_services.models import ReliefAssessment


class ReliefAssessmentRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Emergency Social Services Add-ON'

    url = {
        'add': lazy_reverse('social-services.form'),
        'search': lazy_reverse('social-services.map'),
    }

site.register(ReliefAssessment, ReliefAssessmentRegistry)
