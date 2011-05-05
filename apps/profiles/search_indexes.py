from haystack import indexes
from haystack import site
from profiles.models import Profile
from perms.object_perms import ObjectPermission

class ProfileIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user', faceted=True)
    company = indexes.CharField(model_attr='company')
    address = indexes.CharField(model_attr='address')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zipcode = indexes.CharField(model_attr='zipcode')
    country = indexes.CharField(model_attr='country')
    
    user_object = indexes.CharField(model_attr='user', faceted=True)
    
    # authority fields
    hide_in_search = indexes.BooleanField(model_attr='hide_in_search')
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view')
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view')
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view')
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'
    
    def prepare_user_object(self, obj):
        return obj.user.username
            
    def prepare_user(self, obj):
        return "%s, %s (%s)" % (obj.user.last_name, obj.user.first_name, obj.user.username)
    
    def get_queryset(self):
        return Profile.objects.all().order_by('user')
    
site.register(Profile, ProfileIndex)
