from django.contrib import admin
from tendenci.apps.profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    pass

#admin.site.register(Profile, ProfileAdmin)
