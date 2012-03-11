from registry import site
from registry.base import LogRegistry, lazy_reverse
from actions.models import Action

class ActionRegistry(LogRegistry):
    # actions (Marketing Actions)
    event_logs = {
        'action':{
            'base':('300000', 'FF0033'), # base
            'add':('301000', 'FF0033'), # add
            'edit':('301100', 'FF3333'), # edit
            'delete':('303000', 'FF0033'), # delete
            'search':('304000', 'FF0033'), # search
            'view':('305000', 'FF0066'), # view
            'submitted':('301001', 'FF0033'), # submitted
            'resend':('301005', 'FF0099'), # resend
        },
    }

site.register(Action, ActionRegistry)

