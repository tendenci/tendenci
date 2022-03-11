from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.discounts.models import Discount
from django.utils.translation import gettext_lazy as _


class DiscountRegistry(CoreRegistry):
    version = '1.0'
    author = _('Tendenci - The Open Source AMS for Associations')
    author_email = 'programmers@tendenci.com'
    description = _('Create and Manage Discount Codes for Your Events')

    url = {
        'add': lazy_reverse('discount.add'),
        'search': lazy_reverse('discounts'),
        'list': lazy_reverse('discounts'),
    }

site.register(Discount, DiscountRegistry)
