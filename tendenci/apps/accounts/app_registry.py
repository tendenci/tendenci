from django.contrib.auth.models import User
from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import LogRegistry

class AccountRegistry(LogRegistry):
    """User related logs
    The logs here are not limited to the accounts app
    """

    event_logs = {
        'account':{
            'login':('125200', '66CCFF'), # accounts app
            'impersonation':('1080000', 'FF0000'), # perms app
        },
    }

site.register(User, AccountRegistry)
