from haystack import indexes
from haystack import site

from tendenci.addons.corporate_memberships.models import CorpMembership
from tendenci.core.perms.indexes import TendenciBaseSearchIndex


class CorpMembershipIndex(TendenciBaseSearchIndex):
    corporate_membership_type = indexes.CharField(model_attr='corporate_membership_type')
    authorized_domains = indexes.MultiValueField(null=True)
    reps = indexes.MultiValueField(null=True)
    join_dt = indexes.DateTimeField(model_attr='join_dt')
    renew_dt = indexes.DateTimeField(model_attr='renew_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    is_join_pending = indexes.IntegerField(model_attr='is_join_pending', default=0)
    is_renewal_pending = indexes.IntegerField(model_attr='is_renewal_pending', default=0)
    is_pending = indexes.IntegerField(model_attr='is_pending', default=0)

    def prepare_authorized_domains(self, obj):
        if obj.corp_profile.authorized_domains:
            return list(obj.corp_profile.authorized_domains.all())
        return None

    def prepare_reps(self, obj):
        if obj.corp_profile.reps:
            return [rep.user for rep in obj.corp_profile.reps.all()]
        return None

    def prepare_corporate_membership_type(self, obj):
        return obj.corporate_membership_type.name

    def prepare_corp_app(self, obj):
        return obj.corp_app.name

site.register(CorpMembership, CorpMembershipIndex)
