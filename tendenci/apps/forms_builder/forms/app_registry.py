from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.forms_builder.forms.models import Form
from tendenci.apps.theme.templatetags.static import static


class FormRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create custom forms to take information throughout the site')
    icon = static('images/icons/cms-forms-color-64x64.png')

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
