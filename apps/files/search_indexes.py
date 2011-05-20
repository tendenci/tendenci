from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from files.models import File
from perms.object_perms import ObjectPermission


class FileIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    file = indexes.CharField(model_attr='file')
    description = indexes.CharField(model_attr='description')
    update_dt = indexes.DateTimeField(model_attr='update_dt', null=True)

    # TendenciBaseModel Fields
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

    # permission fields
    users_can_view = indexes.MultiValueField()
    groups_can_view = indexes.MultiValueField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

    def prepare_users_can_view(self, obj):
        return ObjectPermission.objects.users_with_perms('files.view_file', obj)

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('files.view_file', obj)

site.register(File, FileIndex)
