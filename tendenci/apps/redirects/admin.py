from django.contrib import admin

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.redirects.models import Redirect
from tendenci.apps.redirects.forms import RedirectForm

class RedirectAdmin(TendenciBaseModelAdmin):
    list_display = ['from_url','to_url', 'status']
    list_filter = ['from_url', 'status', ]
    search_fields = ['from_url', 'to_url', 'status']
    form = RedirectForm
    ordering = ['-update_dt']

admin.site.register(Redirect, RedirectAdmin)
