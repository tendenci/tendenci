from django.conf.urls import include, url

from .api import SafeApi
from .settings.resources import SettingResource
from .users.resources import UserResource
from .profiles.resources import ProfileResource
from .discounts.resources import DiscountResource
from .entities.resources import EntityResource
from .payments.resources import PaymentMethodResource
from .memberships.resources import (MembershipResource, MembershipTypeResource,
    AppResource)
from .events.resources import (EventResource, TypeResource, PlaceResource)

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

urlpatterns = [
    url(r'^', include(api.urls)),
]
