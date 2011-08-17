from registry import site
from registry.base import CoreRegistry, lazy_reverse
from models import Discount


class DiscountRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create discounts for invoices'
    
    url = {
        'add': lazy_reverse('discount.add'),
        'search': lazy_reverse('discount.search'),
    }

site.register(Discount, DiscountRegistry)
