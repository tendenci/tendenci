from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.forms_builder.forms.models import Form


class FormRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Create custom forms to take information throughout the site')
    icon = '%simages/icons/cms-forms-color-64x64.png' % settings.STATIC_URL

    event_logs = {
        'form': {
            'base': ('587000', '33FFFF'),
            'add': ('587100', '33FFE6'),
            'edit': ('587200', '33FFCC'),
            'delete': ('587300', '33FFB3'),
            'search': ('587400', '33FF99'),
            'view': ('587500', '33FF80'),
            'export': ('587600', '33FF33'),
        }
    }

    url = {
        'add': lazy_reverse('admin:forms_form_add'),
        'search': lazy_reverse('forms'),
        'list': lazy_reverse('forms'),
    }

site.register(Form, FormRegistry)
