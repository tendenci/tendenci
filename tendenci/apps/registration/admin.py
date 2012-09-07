from django.contrib import admin
from tendenci.core.registry import admin_registry

from tendenci.apps.registration.models import RegistrationProfile


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'activation_key_expired')
    search_fields = ('user__username', 'user__first_name')


#admin_registry.site.register(RegistrationProfile, RegistrationAdmin)
