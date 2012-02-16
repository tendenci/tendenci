from django.conf.urls.defaults import *

from api_tasty.api import SafeApi
from api_tasty.settings.resources import SettingResource
from api_tasty.users.resources import UserResource
from api_tasty.profiles.resources import ProfileResource
from api_tasty.discounts.resources import DiscountResource
from api_tasty.entities.resources import EntityResource
from api_tasty.memberships.resources import MembershipResource

api = SafeApi(api_name='v1')
api.register(UserResource())
api.register(EntityResource())
api.register(ProfileResource())
api.register(MembershipResource())
api.register(SettingResource())
api.register(DiscountResource())

urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
