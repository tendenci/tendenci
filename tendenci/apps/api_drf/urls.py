import importlib
from django.urls import include, path
from django.apps import apps

from .api_router import router

#from . import views
from .entities.views import EntityViewSet
from .users.views import UserViewSet
from .groups.views import GroupViewSet
from .memberships.views import MembershipViewSet, MembershipTypeViewSet
from .events.views import EventViewSet

router.register(r"entities", EntityViewSet)
router.register(r"events", EventViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"memberships", MembershipViewSet)
router.register(r"membership_types", MembershipTypeViewSet)
router.register(r"users", UserViewSet)



for app_config in apps.get_app_configs():
    app_name = app_config.name
    if app_name.startswith('addons.'):
        # import addons.xxx.drf.urls
        try:
            importlib.import_module(f"{app_name}.drf.urls")
        except ImportError:
            pass

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    #path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
