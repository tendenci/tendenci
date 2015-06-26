from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import LogRegistry, lazy_reverse
from tendenci.apps.make_payments.models import MakePayment

class MakePaymentRegistry(LogRegistry):
    event_logs = {
        'make_payment':{
            'base':('670000','66CC00'), # base
            'add':('671000','66CC00'), # add
            'edit':('672000','66CC33'), # edit
            'delete':('673000','66CC66'), # delete
            'search':('674000','66FF00'), # search
            'view':('675000','66FF33'), # view
        },
    }

site.register(MakePayment, MakePaymentRegistry)


