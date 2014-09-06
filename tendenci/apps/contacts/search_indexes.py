from haystack import indexes
from haystack import site

from tendenci.apps.contacts.models import Contact
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class ContactIndex(TendenciBaseSearchIndex):
    pass

site.register(Contact, ContactIndex)
