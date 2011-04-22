from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from donations.models import Donation
from perms.models import ObjectPermission

class DonationIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    
    donation_amount = indexes.FloatField(model_attr='donation_amount')
    allocation = indexes.CharField(model_attr='allocation')
    payment_method = indexes.CharField(model_attr='payment_method')
    company = indexes.CharField(model_attr='company')
    address = indexes.CharField(model_attr='address')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zip_code = indexes.CharField(model_attr='zip_code')
    country = indexes.CharField(model_attr='country')
    email = indexes.CharField(model_attr='email')
    phone = indexes.CharField(model_attr='phone')
    
    # authority fields
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    
    who_can_view = indexes.CharField()
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'create_dt'

    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('donations.view_donation', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
    
site.register(Donation, DonationIndex)
