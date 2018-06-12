from django.contrib import admin
from tendenci.apps.donations.models import Donation
from tendenci.apps.donations.forms import DonationAdminForm

class DonationAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'donation_amount', 'payment_method']
    list_display_links = ['first_name']
    form = DonationAdminForm

admin.site.register(Donation, DonationAdmin)
