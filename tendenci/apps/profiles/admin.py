from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from tendenci.apps.profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    pass

#admin.site.register(Profile, ProfileAdmin)

class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        # Removing the permission part
        # (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Permissions'), {'fields': ('user_permissions',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
