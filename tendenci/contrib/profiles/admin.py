from django.contrib import admin

from tendenci.contrib.profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    pass

#admin.site.register(Profile, ProfileAdmin)