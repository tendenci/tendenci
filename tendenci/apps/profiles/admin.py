from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from tendenci.core.registry import admin_registry
from tendenci.apps.profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    pass

#admin_registry.site.register(Profile, ProfileAdmin)
admin_registry.site.register(User, UserAdmin)