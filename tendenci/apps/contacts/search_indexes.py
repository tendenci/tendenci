from haystack import indexes


from tendenci.apps.contacts.models import Contact
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class ContactIndex(TendenciBaseSearchIndex, indexes.Indexable):

    def get_model(self):
        return Contact


