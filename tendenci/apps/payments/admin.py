from django.contrib import admin
from tendenci.apps.payments.models import Payment, PaymentMethod


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['response_code', 'response_reason_text', 'auth_code', 'trans_id']


class PaymentMethodAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['id', 'human_name', 'machine_name', 'is_online', 'admin_only']
    list_display_links = ('human_name',)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
