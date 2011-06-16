from django.utils.html import strip_tags, strip_entities

from haystack import indexes, site
from memberships.models import App, AppEntry, Membership, MembershipArchive
from perms.indexes import TendenciBaseSearchIndex


class MembershipIndex(TendenciBaseSearchIndex):
    corporate_membership_id = indexes.BooleanField(model_attr='corporate_membership_id')

class MembershipArchiveIndex(TendenciBaseSearchIndex):
    corporate_membership_id = indexes.BooleanField(model_attr='corporate_membership_id')

class MemberAppIndex(TendenciBaseSearchIndex):
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description


class MemberAppEntryIndex(TendenciBaseSearchIndex):
    entry_time = indexes.DateTimeField(model_attr='entry_time')
    
    def get_updated_field(self):
        return 'entry_time'


site.register(Membership, MembershipIndex)
site.register(MembershipArchive, MembershipArchiveIndex)
site.register(App, MemberAppIndex)
site.register(AppEntry, MemberAppEntryIndex)
