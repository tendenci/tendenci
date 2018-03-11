from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import LogRegistry
from tendenci.apps.recurring_payments.models import RecurringPayment

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
