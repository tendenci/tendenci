from haystack import indexes
from haystack import site
from user_groups.models import Group
from perms.object_perms import ObjectPermission


class GroupIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    label = indexes.CharField(model_attr='label')
    type = indexes.CharField(model_attr='type')
    description = indexes.CharField(model_attr='description')

    # TendenciBaseModel Fields
    show_as_option = indexes.BooleanField(model_attr='show_as_option')
    allow_self_add = indexes.BooleanField(model_attr='allow_self_add')
    allow_self_remove = indexes.BooleanField(model_attr='allow_self_remove')
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view')
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view')
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view')
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')

    # permission fields
    users_can_view = indexes.MultiValueField()
    groups_can_view = indexes.MultiValueField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_users_can_view(self, obj):
        return ObjectPermission.objects.users_with_perms('user_groups.view_group', obj)

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('user_groups.view_group', obj)

site.register(Group, GroupIndex)
