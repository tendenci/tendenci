from django.conf.urls.defaults import *

from tendenci.core.api_tasty.api import SafeApi
from tendenci.core.api_tasty.settings.resources import SettingResource
from tendenci.core.api_tasty.users.resources import UserResource
from tendenci.core.api_tasty.profiles.resources import ProfileResource
from tendenci.core.api_tasty.discounts.resources import DiscountResource
from tendenci.core.api_tasty.entities.resources import EntityResource
from tendenci.core.api_tasty.payments.resources import PaymentMethodResource
from tendenci.core.api_tasty.memberships.resources import (MembershipResource,
    MembershipTypeResource, AppResource)
from tendenci.core.api_tasty.events.resources import (EventResource, TypeResource,
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
