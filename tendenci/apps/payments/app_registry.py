from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import LogRegistry, lazy_reverse
from tendenci.apps.payments.models import Payment


class PaymentRegistry(LogRegistry):
    # payments - PINK ORANGE base - complement is ????
    event_logs = {
        'payments':{
            'base':('280000', 'FF6666'), # base
            'add':('281000', 'FF6666'), # add
            'edit':('282000', 'FF6666'), # edit
            'delete':('283000', 'FF6666'), # delete
            'search':('284000', 'FF6666'), # search
            'view':('285000', 'FF6666'), # view
            'export':('286000', 'FF6666'), # export
            'edit_credit_card_approved':('282101', 'FF6666'), # Edit - Credit card approved
            'edit_credit_card_declined':('282102', 'FF6666'), # Edit - Credit card declined
        },
    }

site.register(Payment, PaymentRegistry)
