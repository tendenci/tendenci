from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from .models import StripeAccount, Charge

class StripeAccountAdmin(TendenciBaseModelAdmin):
    list_display = ('account_name', 'email', 'default_currency', 'stripe_user_id', 'scope',
                     'status_detail')
    list_filter = ('status_detail',)
    search_fields = ('account_name', 'email')
    readonly_fields=('stripe_user_id', 'scope')
    fields = ('account_name', 'email', 'default_currency',
              'stripe_user_id', 'scope',
            'status_detail')
    ordering = ['-update_dt']

    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('stripe_connect.authorize'))


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'amount', 'charge_dt')
    list_filter = ('account',)
    ordering = ['-charge_dt']
    
    actions = None

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('admin:stripe_charge_changelist'))


admin.site.register(StripeAccount, StripeAccountAdmin)
admin.site.register(Charge, ChargeAdmin)
