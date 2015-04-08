from haystack import indexes


from tendenci.apps.profiles.models import Profile
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class ProfileIndex(TendenciBaseSearchIndex, indexes.Indexable):
    user = indexes.CharField(model_attr='user', faceted=True)
    user_object = indexes.CharField(model_attr='user', faceted=True)
    display_name = indexes.CharField(model_attr='display_name')
    company = indexes.CharField(model_attr='company')
    address = indexes.CharField(model_attr='address')
    city = indexes.CharField(model_attr='city')
    state = indexes.CharField(model_attr='state')
    zipcode = indexes.CharField(model_attr='zipcode')
    country = indexes.CharField(model_attr='country')
    last_name = indexes.CharField(faceted=True)
    hide_in_search = indexes.BooleanField(model_attr='hide_in_search', null=True)

    @classmethod
    def get_model(self):
        return Profile

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

    def index_queryset(self, using=None):
        return self.get_model()._default_manager.all().order_by('user')

# Removed from index after search view was updated to perform
# all searches on the database.
#
