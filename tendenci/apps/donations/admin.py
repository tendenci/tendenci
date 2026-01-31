from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect

from tendenci.apps.donations.models import Donation
from tendenci.apps.donations.forms import DonationAdminForm

class DonationAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'show_user', 'donation_amount', 'donate_to_entity', 'payment_method']
    #list_display_links = ['first_name']
    list_filter = (('donate_to_entity', admin.RelatedOnlyFieldListFilter),
                  ('user', admin.RelatedOnlyFieldListFilter),
                   )
    autocomplete_fields = ('user',)
    form = DonationAdminForm
    
    @mark_safe
    def show_user(self, instance):
        if instance.user:
            return '<a href="{0}" title="Donor">{1}</a>'.format(
                    reverse('profile', args=[instance.user.username]),
                    instance.user.username
                )
        return ""
    show_user.short_description = 'User'
    show_user.allow_tags = True
    show_user.admin_order_field = 'user__username'

    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(
                    reverse('donation.add')
                )


admin.site.register(Donation, DonationAdmin)
