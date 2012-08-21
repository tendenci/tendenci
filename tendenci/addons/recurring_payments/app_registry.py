from tendenci.core.registry import site
from tendenci.core.registry.base import LogRegistry, lazy_reverse
from tendenci.addons.recurring_payments.models import RecurringPayment

class RecurringPaymentRegistry(LogRegistry):
    # recurring payments - green
    event_logs = {
        'recurring_payment':{
            'base':('1120000', '1A7731'), #base
            'add':('1120100', '14A037'), # add
            'edit':('1120200', '478256'), # edit
            'delete':('1120300', '8FBA9A'), # delete
            'search':('1120400', '14E548'), # search
            'disable':('1120500', '339B41'), # disable
        },
    }

site.register(RecurringPayment, RecurringPaymentRegistry)

