from django.conf.urls import *

from tendenci.apps.api_tasty.api import SafeApi
from tendenci.apps.api_tasty.settings.resources import SettingResource
from tendenci.apps.api_tasty.users.resources import UserResource
from tendenci.apps.api_tasty.profiles.resources import ProfileResource
from tendenci.apps.api_tasty.discounts.resources import DiscountResource
from tendenci.apps.api_tasty.entities.resources import EntityResource
from tendenci.apps.api_tasty.payments.resources import PaymentMethodResource
from tendenci.apps.api_tasty.memberships.resources import (MembershipResource,
    MembershipTypeResource, AppResource)
from tendenci.apps.api_tasty.events.resources import (EventResource, TypeResource,
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
