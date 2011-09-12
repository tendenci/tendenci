from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Invoice


class InvoiceRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Invoices for the entire system'
    icon = '/site_media/static/images/icons/invoicing-color-64x64.png'
    
    url = {
        'search': lazy_reverse('invoice.search'),
    }

site.register(Invoice, InvoiceRegistry)
