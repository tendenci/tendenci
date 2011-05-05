from haystack import indexes
from haystack import site
from entities.models import Entity
from perms.object_perms import ObjectPermission

class EntityIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    entity_name = indexes.CharField(model_attr='entity_name')
    entity_type = indexes.CharField(model_attr='entity_type') 
    entity_parent_id = indexes.IntegerField(model_attr='entity_parent_id')
    contact_name = indexes.CharField(model_attr='contact_name')
    phone = indexes.CharField(model_attr='phone')
    fax = indexes.CharField(model_attr='fax')
    email = indexes.CharField(model_attr='email')
    website = indexes.CharField(model_attr='website')
    summary = indexes.CharField(model_attr='summary')
    notes = indexes.CharField(model_attr='notes')
    admin_notes = indexes.CharField(model_attr='admin_notes')
    
    # authority fields
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view')
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view')
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view')
    allow_anonymous_edit = indexes.BooleanField(model_attr='allow_anonymous_edit')
    allow_user_edit = indexes.BooleanField(model_attr='allow_user_edit')
    allow_member_edit = indexes.BooleanField(model_attr='allow_member_edit')
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
        users = ObjectPermission.objects.who_has_perm('entities.view_entity', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
    
site.register(Entity, EntityIndex)
