from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.models.functions import Concat
from django.db.models import Value
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.payments.models import Payment, PaymentMethod
from tendenci.apps.theme.templatetags.static import static


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'view_on_site', 'amount',  'show_product', 'payer', 'status_detail', 'invoice_link', 'create_dt', ]
    search_fields = [
        'first_name',
        'last_name',
        'description',
    ]
    fields = ['invoice', 'amount', 'trans_id', 'first_name', 'last_name',
              'company', 'description', 'address', 'city', 'state', 'zip', 
              'country', 'status_detail']
    readonly_fields = ['invoice', 'amount', 'trans_id', 'status_detail']

    @mark_safe
    def view_on_site(self, instance):
        link_icon = static('images/icons/external_16x16.png')
        return f'<a href="{instance.get_absolute_url()}" title="View payment"><img src="{link_icon}" alt="View payment" /></a>'
    view_on_site.short_description = _('view')

    @mark_safe
    def invoice_link(self, instance):
        if instance.invoice:
            invoice_url = instance.invoice.get_absolute_url()
            return f'<a href="{invoice_url}" title="{instance.invoice.title}">{instance.invoice.id}</a>'
        return ""
    invoice_link.short_description = _('Invoice ID')
    invoice_link.allow_tags = True
    invoice_link.admin_order_field = 'invoice'

    @mark_safe
    def show_product(self, instance):
        if instance.invoice:
            obj = instance.invoice.get_object()
            if hasattr(obj, '_meta') and obj._meta.model_name == 'membershipset':
                memberships = obj.memberships()
                result = '{instance.invoice.object_type}:'
                for m in memberships:
                    result += f' <a href="{m.get_absolute_url()}">{m.id}</a>'
                return result
            elif hasattr(obj, 'get_absolute_url'):
                obj_url = obj.get_absolute_url()
                return f'{instance.invoice.object_type}: <a href="{obj_url}">{instance.invoice.get_object()}</a>'
            
            return f'{instance.invoice.object_type}: {instance.invoice.get_object()}'
        return ""
    show_product.short_description = _('Item')
    show_product.allow_tags = True
    show_product.admin_order_field = 'invoice__object_type'

    @mark_safe
    def payer(self, instance):
        if instance:
            if not instance.first_name:
                instance.first_name = ''
            if not instance.last_name:
                instance.last_name = ''
            return f'{instance.first_name} {instance.last_name}'
 
        return ""
    payer.short_description = _('User')
    payer.allow_tags = True
    payer.admin_order_field = Concat('first_name', Value(' '), 'last_name')

    def has_add_permission(self, request):
        return False


class PaymentMethodAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['id', 'human_name', 'machine_name', 'is_online', 'admin_only']
    list_display_links = ('human_name',)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
