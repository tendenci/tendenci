from tendenci.core.registry import site
from tendenci.core.registry.base import LogRegistry, lazy_reverse
from tendenci.apps.accountings.models import Acct


class AccountingRegistry(LogRegistry):
    event_logs = {
        'general ledger': {
            'add': ('312100', '339900'),    # general ledger added
            'edit': ('312200', '339900'),   # general ledger edited
            'delete': ('312300', '339900'),  # general ledger deleted
            'search': ('312400', '339900'),  # general ledger searched
            'viewed': ('312500', '339900'),  # general ledger viewed
        },
        'accounting': {
            'accounting_entry_deleted': ('313300', '669933'),
            'accounting_transaction_deleted': ('313400', '669933'),
            'acct_entry_table_export': ('315105', '669933'),
        },
    }

site.register(Acct, AccountingRegistry)
