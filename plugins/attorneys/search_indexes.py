from haystack import indexes
from haystack import site

from attorneys.models import Attorney
from perms.object_perms import ObjectPermission

class AttorneyIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    category = indexes.CharField(model_attr='category')
    position = indexes.CharField(model_attr='position')
    address = indexes.CharField(model_attr='address')
    address2 = indexes.CharField(model_attr='address2')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zip = indexes.CharField(model_attr='zip')
    phone = indexes.CharField(model_attr='phone')
    fax = indexes.CharField(model_attr='fax')
    email = indexes.CharField(model_attr='email')
    
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
    create_dt = indexes.DateTimeField(model_attr='create_dt', null=True)
    update_dt = indexes.DateTimeField(model_attr='update_dt', null=True)
    
    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')
    
    # permission fields
    users_can_view = indexes.MultiValueField()
    groups_can_view = indexes.MultiValueField()
    
    def prepare_users_can_view(self, obj):
        return ObjectPermission.objects.users_with_perms('before_and_after.view_before_and_after', obj)

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('before_and_after.view_before_and_after', obj)

    def get_updated_field(self):
        return 'update_dt'

site.register(Attorney, AttorneyIndex)
