from datetime import datetime

from django.utils.html import strip_tags, strip_entities
from haystack import indexes
from haystack import site

from quotes.models import Quote
from perms.object_perms import ObjectPermission


class QuoteIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    quote = indexes.CharField(model_attr='quote')
    author = indexes.CharField(model_attr='author')
    source = indexes.CharField(model_attr='source')
    create_dt = indexes.DateTimeField(model_attr='create_dt', null=True)
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

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_quote(self, obj):
        quote = obj.quote
        quote = strip_tags(quote)
        quote = strip_entities(quote)
        return quote

    def prepare_users_can_view(self, obj):
        return ObjectPermission.objects.users_with_perms('quotes.view_quote', obj)

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('quotes.view_quote', obj)

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view \
                and obj.status == 1  and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.create_dt

site.register(Quote, QuoteIndex)
