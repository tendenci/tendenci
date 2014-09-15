from tendenci.core.registry import site
from tendenci.core.registry.base import LogRegistry, lazy_reverse
from tendenci.core.emails.models import Email

class EmailRegistry(LogRegistry):
    event_logs = {
        'email':{
            'base':('130000', 'CC3300'), # base
            'add':('131000', 'CC3300'), # add
            'edit':('132000', 'CC3300'), # edit
            'delete':('133000', 'CC3300'), # delete
            'search':('134000', 'CC3300'), # search
            'view':('135000', 'CC3300'), # view
            'send_failure':('131100', 'CC3366'), # email send failure
            'send_success':('131101', 'CC3399'), # email send success
            'send_success_newsletter':('131102', 'CC33CC'), # email send success - newsletter
            'spam_detected':('130999', 'FF0000'), # email SPAM DETECTED!! (RED - this is important)
        },
    }

site.register(Email, EmailRegistry)

