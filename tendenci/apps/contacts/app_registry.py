from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import LogRegistry
from tendenci.apps.contacts.models import Contact

class ContactRegistry(LogRegistry):
    # contacts - TEAL/LIME-GREEN base
    event_logs = {
        'contact':{
            'add_with_new_user':('125114', '33CCCC'), # add - contact form submitted / new user added
            'add_with_existing_user':('125115', '0066CC'), # add - contact form submitted / user already exists
        },
    }

site.register(Contact, ContactRegistry)
