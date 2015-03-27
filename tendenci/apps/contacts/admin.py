from django.contrib import admin

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from .models import Contact


class ContactAdmin(TendenciBaseModelAdmin):
    model = Contact


admin.site.register(Contact, ContactAdmin)
