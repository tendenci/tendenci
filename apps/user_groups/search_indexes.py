from haystack import indexes
from haystack import site
from user_groups.models import Group
from perms.models import ObjectPermission

class GroupIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    label = indexes.CharField(model_attr='label')
    type = indexes.CharField(model_attr='type')
    description = indexes.CharField(model_attr='description')
   
    # authority fields
    show_as_option = indexes.BooleanField(model_attr='show_as_option')
    allow_self_add = indexes.BooleanField(model_attr='allow_self_add')
    allow_self_remove = indexes.BooleanField(model_attr='allow_self_remove')
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view')
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view')
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view')
    #use_for_membership = indexes.BooleanField(model_attr='use_for_membership')
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    
    who_can_view = indexes.CharField()
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')
    
    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('user_groups.view_group', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''

    
site.register(Group, GroupIndex)
