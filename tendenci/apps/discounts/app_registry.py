from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.discounts.models import Discount
from django.utils.translation import ugettext_lazy as _


class DiscountRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Create and Manage Discount Codes for Your Events')

    url = {
        'add': lazy_reverse('discount.add'),
        'search': lazy_reverse('discounts'),
        'list': lazy_reverse('discounts'),
    }

site.register(Discount, DiscountRegistry)
