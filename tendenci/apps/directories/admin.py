from django.contrib import admin
from tendenci.apps.directories.models import DirectoryPricing
from tendenci.apps.directories.forms import DirectoryPricingForm


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ['headline', 'create_dt']

# admin.site.register(Directory, DirectoryAdmin)

class DirectoryPricingAdmin(admin.ModelAdmin):
    list_display = ['duration', 'regular_price', 'premium_price',
                    'regular_price_member', 'premium_price_member', 'status']
    fieldsets = (
        (None, {'fields': ('duration', 'regular_price', 'premium_price',
                           'regular_price_member', 'premium_price_member', 'status',)}),
    )
    form = DirectoryPricingForm

admin.site.register(DirectoryPricing, DirectoryPricingAdmin)
