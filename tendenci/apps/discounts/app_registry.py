from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.discounts.models import Discount


class DiscountRegistry(CoreRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create and Manage Discount Codes for Your Events'
    
    url = {
        'add': lazy_reverse('discount.add'),
        'search': lazy_reverse('discounts'),
        'list': lazy_reverse('discounts'),
    }

site.register(Discount, DiscountRegistry)
