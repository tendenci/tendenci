from tendenci.core.registry import site
from tendenci.core.registry.base import LogRegistry, lazy_reverse
from tendenci.core.email_blocks.models import EmailBlock

class EmailBlockRegistry(LogRegistry):
    event_logs = {
        'email_block':{
            'base':('135000', 'CC3300'), # base
            'add':('135100', 'CC3300'), # add
            'edit':('135300', 'CC3300'), # edit
            'delete':('135300', 'CC3300'), # delete
            'search':('135400', 'CC3300'), # search
            'view':('135550', 'CC3300'), # view
        },
    }

site.register(EmailBlock, EmailBlockRegistry)

