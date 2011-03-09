from haystack import indexes
from haystack import site
from corporate_memberships.models import CorporateMembership

class CorporateMembershipIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    corporate_membership_type = indexes.CharField(model_attr='corporate_membership_type')
    name = indexes.CharField(model_attr='name', faceted=True)
    #name = indexes.CharField(model_attr='name', index_fieldname='corp_name', faceted=True)
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
    
    # authority fields
    create_dt = indexes.DateTimeField(model_attr='create_dt')
    creator = indexes.CharField(model_attr='creator', null=True)
    creator_username = indexes.CharField(model_attr='creator_username', default='')
    owner = indexes.CharField(model_attr='owner', null=True)
    owner_username = indexes.CharField(model_attr='owner_username', default='')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')
    
    
    def prepare_authorized_domains(self, obj):
        if obj.auth_domains:
            return list(obj.auth_domains.all())
        
    def prepare_reps(self, obj):
        if obj.reps:
            return [rep.user for rep in obj.reps.all()]
    
    def prepare_corporate_membership_type(self, obj):
        if obj.corporate_membership_type:
            return obj.corporate_membership_type.name
        
    def prepare_corp_app(self, obj):
        if obj.corp_app:
            return obj.corp_app.name

site.register(CorporateMembership, CorporateMembershipIndex)
