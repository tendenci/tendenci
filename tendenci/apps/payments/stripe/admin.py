from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from .models import StripeAccount, Charge
from .forms import StripeAccountForm

       
class StripeAccountAdmin(TendenciBaseModelAdmin):
    list_display = ('stripe_user_id', 'account_name',
                    'show_entity', 
                    'email', 'default_currency', 'scope',
                     'status_detail', 'action')
    list_filter = ('status_detail',)
    search_fields = ('account_name', 'email')
    readonly_fields=('stripe_user_id', 'scope', 'status_detail')
    fields = ('stripe_user_id', 'scope',
              'account_name', 'email', 
              'entity',
            'default_currency',
            'status_detail')
    ordering = ['-update_dt']
    form = StripeAccountForm

    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('stripe_connect.acct_onboarding'))

    @mark_safe
    def show_entity(self, instance):
        if instance and instance.entity:
            url = reverse('admin:entities_entity_change',
                            args=[instance.id])
            return f'<a href="{url}">{instance.entity}</a>'
        return '-'
    show_entity.short_description = _('Entity')
    show_entity.admin_order_field = 'entity__entity_name'
    
    @mark_safe
    def action(self, instance):
        if instance and instance.status_detail == 'not completed':
            url = reverse('stripe_connect.acct_onboarding_refresh', args=[instance.id])
            return f'<a href="{url}">Continue Onboarding</a>'
        return '-'


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
