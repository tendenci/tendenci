from django.contrib import admin
from payments.models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['response_code', 'response_reason_text', 'auth_code', 'trans_id']

admin.site.register(Payment, PaymentAdmin)