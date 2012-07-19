from haystack import indexes
from haystack import site
from corporate_memberships.models import CorporateMembership, CorpMembRenewEntry
from perms.indexes import TendenciBaseSearchIndex

class CorporateMembershipIndex(TendenciBaseSearchIndex):
    corporate_membership_type = indexes.CharField(model_attr='corporate_membership_type')
    name = indexes.CharField(model_attr='name', faceted=True)
    address = indexes.CharField(model_attr='address', default='')
    address2 = indexes.CharField(model_attr='address2', default='')
    city = indexes.CharField(model_attr='city', default='')
    state = indexes.CharField(model_attr='state', default='')
    zip = indexes.CharField(model_attr='zip', default='')
    country = indexes.CharField(model_attr='country', default='')
    phone = indexes.CharField(model_attr='phone', default='')
    email = indexes.CharField(model_attr='email', default='')
    authorized_domains = indexes.MultiValueField(null=True)
    reps = indexes.MultiValueField(null=True)
    secret_code = indexes.CharField(model_attr='secret_code', null=True)
    corp_app = indexes.CharField(model_attr='corp_app')
    join_dt = indexes.DateTimeField(model_attr='join_dt')
    renew_dt = indexes.DateTimeField(model_attr='renew_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    renew_entry_id = indexes.IntegerField(model_attr='renew_entry_id', null=True)
    is_join_pending = indexes.IntegerField(model_attr='is_join_pending', default=0)
    is_renewal_pending = indexes.IntegerField(model_attr='is_renewal_pending', default=0)
    is_pending = indexes.IntegerField(model_attr='is_pending', default=0)

    def prepare_authorized_domains(self, obj):
        if obj.auth_domains:
            return list(obj.auth_domains.all())
        return None

    def prepare_reps(self, obj):
        if obj.reps:
            return [rep.user for rep in obj.reps.all()]
        return None

    def prepare_corporate_membership_type(self, obj):
        return obj.corporate_membership_type.name

    def prepare_corp_app(self, obj):
        return obj.corp_app.name

site.register(CorporateMembership, CorporateMembershipIndex)
