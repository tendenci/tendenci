from django.contrib import admin

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.redirects.models import Redirect
from tendenci.apps.redirects.forms import RedirectForm

class RedirectAdmin(TendenciBaseModelAdmin):
    list_display = [ ]
    form = RedirectForm
    ordering = ['-update_dt']

admin.site.register(Redirect, RedirectAdmin)