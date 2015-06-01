from haystack import indexes

from django.db.models import signals
from django.conf import settings

from tendenci.apps.perms.object_perms import ObjectPermission
#from tendenci.apps.search.indexes import CustomSearchIndex

def is_whoosh():
    default_engine = settings.HAYSTACK_CONNECTIONS.get('default', {}).get('ENGINE', '')
    return default_engine and 'whoosh' in default_engine.lower()

class TendenciBaseSearchIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    # TendenciBaseModel Fields
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view', null=True)
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view', null=True)
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view', null=True)
    # allow_anonymous_edit = indexes.BooleanField(model_attr='allow_anonymous_edit')
    allow_user_edit = indexes.BooleanField(model_attr='allow_user_edit', null=True)
    allow_member_edit = indexes.BooleanField(model_attr='allow_member_edit', null=True)
    creator = indexes.CharField(model_attr='creator', null=True)
    creator_username = indexes.CharField(model_attr='creator_username', null=True)
    owner = indexes.CharField(model_attr='owner', null=True)
    owner_username = indexes.CharField(model_attr='owner_username', null=True)
    status = indexes.BooleanField(model_attr='status', null=True)
    status_detail = indexes.CharField(model_attr='status_detail')
    create_dt = indexes.DateTimeField(model_attr='create_dt', null=True)
    update_dt = indexes.DateTimeField(model_attr='update_dt', null=True)

    # permission fields
    users_can_view = indexes.MultiValueField(null=True)
    groups_can_view = indexes.MultiValueField(null=True)

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    # add order field for sorting. the subclasses can override
    # the prepare_order method to sort by a different field
    order = indexes.DateTimeField()

    def get_model(self):
        return None

    def prepare_allow_anonymous_view(self, obj):
        if is_whoosh():
            try:
                temp = int(obj.allow_anonymous_view)
            except TypeError:
                temp = 0
            return temp
        return obj.allow_anonymous_view

    def prepare_allow_user_view(self, obj):
        if is_whoosh():
            try:
                temp = int(obj.allow_user_view)
            except TypeError:
                temp = 0
            return temp
        return obj.allow_user_view

    def prepare_allow_member_view(self, obj):
        if is_whoosh():
            try:
                temp = int(obj.allow_member_view)
            except TypeError:
                temp = 0
            return temp
        return obj.allow_member_view

    def prepare_allow_user_edit(self, obj):
        if is_whoosh():
            try:
                temp = int(obj.allow_user_edit)
            except TypeError:
                temp = 0
            return temp
        return obj.allow_user_edit

    def prepare_allow_member_edit(self, obj):
        if is_whoosh():
            try:
                temp = int(obj.allow_member_edit)
            except TypeError:
                temp = 0
            return temp
        return obj.allow_member_edit

    def prepare_status(self, obj):
        if is_whoosh():
            try:
                temp = int(obj.status)
            except TypeError:
                temp = 0
            return temp
        return obj.status

    def prepare_order(self, obj):
        return obj.create_dt

    def get_updated_field(self):
        return 'update_dt'

    def prepare_users_can_view(self, obj):
        """
        This needs to be overwritten if 'view' permission label does not follow the standard convention:
        (app_label).view_(module_name)
        """
        return ObjectPermission.objects.users_with_perms('%s.view_%s' % (obj._meta.app_label, obj._meta.model_name), obj)

    def prepare_groups_can_view(self, obj):
        """
        This needs to be overwritten if 'view' permission label does not follow the standard convention:
        (app_label).view_(module_name)
        """
        return ObjectPermission.objects.groups_with_perms('%s.view_%s' % (obj._meta.app_label, obj._meta.model_name), obj)

