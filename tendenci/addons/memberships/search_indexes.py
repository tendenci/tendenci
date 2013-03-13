from haystack import indexes, site

from django.utils.html import strip_tags, strip_entities

from tendenci.addons.memberships.models import App, AppEntry, MembershipDefault
from tendenci.core.perms.indexes import TendenciBaseSearchIndex


class MembershipDefaultIndex(TendenciBaseSearchIndex):
    corporate_membership_id = indexes.IntegerField(model_attr='corporate_membership_id', null=True)
    member_number = indexes.CharField(model_attr='member_number')
    membership_type = indexes.IntegerField()
    first_name = indexes.CharField(null=True)
    last_name = indexes.CharField(null=True)
    email = indexes.CharField(null=True)

    def prepare_membership_type(self, obj):
        pk = obj.membership_type.pk
        return pk

    def prepare_first_name(self, obj):
        first_name = obj.user.first_name
        return first_name

    def prepare_last_name(self, obj):
        last_name = obj.user.last_name
        return last_name

    def prepare_email(self, obj):
        email = obj.user.email
        return email


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


site.register(App, MemberAppIndex)
site.register(AppEntry, MemberAppEntryIndex)
site.register(MembershipDefault, MembershipDefaultIndex)
