from haystack import indexes
from haystack import site
from contacts.models import Contact
from perms.indexes import TendenciBaseSearchIndex


class ContactIndex(TendenciBaseSearchIndex):
    pass

site.register(Contact, ContactIndex)
