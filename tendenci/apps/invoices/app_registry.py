from django.utils.translation import ugettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.theme.templatetags.static import static


class InvoiceRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Invoices for the entire system')
    icon = static('images/icons/invoicing-color-64x64.png')

    event_logs = {
        'invoices':{
            'base':('310000', '006666'), # base
            'add':('311000', '006666'), # add
            'edit':('312000', '006633'), # edit
            'delete':('313000', '006600'), # delete
            'search':('314000', '009900'), # search
            'view':('315000', '009933'), # view
            'adjusted':('311220', 'FF0000'), # invoice adjusted - RED!!!
        },
    }

    url = {
        'search': lazy_reverse('invoice.search'),
    }

site.register(Invoice, InvoiceRegistry)
