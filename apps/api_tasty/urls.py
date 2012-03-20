from django.conf.urls.defaults import *

from api_tasty.api import SafeApi
from api_tasty.settings.resources import SettingResource
from api_tasty.users.resources import UserResource
from api_tasty.profiles.resources import ProfileResource
from api_tasty.discounts.resources import DiscountResource
from api_tasty.entities.resources import EntityResource
from api_tasty.payments.resources import PaymentMethodResource
from api_tasty.memberships.resources import (MembershipResource, 
    MembershipTypeResource, AppResource)
from api_tasty.events.resources import (EventResource, TypeResource,
    PlaceResource)

api = SafeApi(api_name='v1')
# user profiles
api.register(UserResource())
api.register(EntityResource())
api.register(ProfileResource())
# memberships
api.register(MembershipResource())
api.register(MembershipTypeResource())
api.register(AppResource())
# settings
api.register(SettingResource())
# discounts
api.register(DiscountResource())
# payments
api.register(PaymentMethodResource())
# events
api.register(EventResource())
api.register(TypeResource())
api.register(PlaceResource())

urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
