from django.contrib.auth.models import User
from registry import site
from registry.base import LogRegistry, lazy_reverse

class AccountRegistry(LogRegistry):
    """User related logs
    The logs here are not limited to the accounts app
    """
    
    event_logs = {
        'account':{
            'login':('125200', '66CCFF'), # accounts app
            'impersonation':('1080000', 'FF0000'), # perms app
            'homepage':('100000', '7F0000'), # base app
        },
    }

site.register(User, AccountRegistry)

