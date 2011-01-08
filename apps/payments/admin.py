from django.contrib import admin
from payments.models import Payment, PaymentMethod

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['response_code', 'response_reason_text', 'auth_code', 'trans_id']

class PaymentMethodAdmin(admin.ModelAdmin):
    pass

admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)