from django.contrib import admin

from corporate_memberships.models import CorporateMembershipType
from corporate_memberships.forms import CorporateMembershipTypeForm

class CorporateMembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'renewal_price', 'membership_type',  
                     'admin_only', 'status_detail', 'order']
    list_filter = ['name', 'price', 'status_detail']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'renewal_price', 'membership_type', 'description')}),
        ('Individual Pricing Options', {'fields': ('apply_threshold', 'individual_threshold',
                                                   'individual_threshold_price',)}),
        ('Other Options', {'fields': (
            'order', ('admin_only', 'status'), 'status_detail')}),
    )
    
    form = CorporateMembershipTypeForm
    
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
 
        # save the object
        instance.save()
        
        #form.save_m2m()
        
        return instance


admin.site.register(CorporateMembershipType, CorporateMembershipTypeAdmin)