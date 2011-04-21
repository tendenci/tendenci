from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from locations.models import Location
from perms.models import ObjectPermission

class LocationIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    description = indexes.CharField(model_attr='description')
    location_name = indexes.CharField(model_attr='location_name')
    create_dt = indexes.DateTimeField(model_attr='create_dt', null=True)

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
        return 'update_dt'
    
    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('locations.view_location', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
    
    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
    
site.register(Location, LocationIndex)
