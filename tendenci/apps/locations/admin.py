from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.addons.locations.models import Location
from tendenci.addons.locations.forms import LocationForm

class LocationAdmin(TendenciBaseModelAdmin):
    list_display = ['location_name', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status_detail', 'owner_username']
    prepopulated_fields = { }#'slug': ['title']}
    search_fields = ['title', 'description']
    fieldsets = (
        (_('Location Information'), {
            'fields': ('location_name',
#                       'slug',
                       'description',
                       'latitude',
                       'longitude',
#                       'photo_upload',
                       'hq',
            )
        }),
        (_('Contact'), {
            'fields': ('contact',
                       'address',
                       'address2',
                       'city',
                       'state',
                       'zipcode',
                       'country',
                       'phone',
                       'fax',
                       'email',
                       'website',
            )
        }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Status'), {'fields': (
            'status_detail',
            )}),
        )
    form = LocationForm
    ordering = ['-update_dt']

admin.site.register(Location, LocationAdmin)
