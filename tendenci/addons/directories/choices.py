from django.utils.translation import ugettext_lazy as _

DURATION_CHOICES = (
    (14, _('14 Days from Activation date')),
    (60, _('60 Days from Activation date')),
    (90,_('90 Days from Activation date')),
    (120,_('120 Days from Activation date')),
    (365,_('1 Year from Activation date')),
)
ADMIN_DURATION_CHOICES = (
    (0, _('Unlimited')),
    (14,_('14 Days from Activation date')),
    (30,_('30 Days from Activation date')),
    (60,_('60 Days from Activation date')),
    (90,_('90 Days from Activation date')),
    (120,_('120 Days from Activation date')),
    (365,_('1 Year from Activation date')),
)

STATUS_CHOICES = (
    (1, _('Active')),
    (0, _('Inactive')),
)
