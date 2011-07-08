from haystack import indexes
from haystack import site
from profiles.models import Profile
from perms.indexes import TendenciBaseSearchIndex


class ProfileIndex(TendenciBaseSearchIndex):
    user = indexes.CharField(model_attr='user', faceted=True)
    company = indexes.CharField(model_attr='company')
    address = indexes.CharField(model_attr='address')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zipcode = indexes.CharField(model_attr='zipcode')
    country = indexes.CharField(model_attr='country')
    user_object = indexes.CharField(model_attr='user', faceted=True)
    last_name = indexes.CharField(faceted=True)

    def prepare_last_name(self, obj):
        return obj.user.last_name

    def prepare_user_object(self, obj):
        return obj.user.username

    def prepare_user(self, obj):
        return "%s, %s (%s)" % (
            obj.user.last_name,
            obj.user.first_name,
            obj.user.username
        )

    def index_queryset(self):
        return Profile.objects.all().order_by('user')

site.register(Profile, ProfileIndex)
