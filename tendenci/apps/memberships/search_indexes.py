from haystack import indexes

from tendenci.apps.memberships.models import MembershipDefault
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class MembershipDefaultIndex(TendenciBaseSearchIndex, indexes.Indexable):
    corporate_membership_id = indexes.IntegerField(model_attr='corporate_membership_id', null=True)
    member_number = indexes.CharField(model_attr='member_number')
    membership_type = indexes.IntegerField()
    first_name = indexes.CharField(null=True)
    last_name = indexes.CharField(null=True)
    email = indexes.CharField(null=True)

    @classmethod
    def get_model(self):
        return MembershipDefault

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



# Removed from index after search view was updated to perform
# all searches on the database.
# site.register(AppEntry, MemberAppEntryIndex)
#
