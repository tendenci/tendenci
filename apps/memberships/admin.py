from django.contrib import admin
from django.conf import settings
from memberships.models import MembershipType
from memberships.forms import MembershipTypeForm

class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'admin_fee', 'group', 'require_approval',
                     'renewal', 'expiration_method', 'corporate_membership_only',
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'admin_fee', 'description', 'group')}),
        ('Expiration Method', {'fields': (
            ('type_exp_method'),)}),
        ('Other Options', {'fields': (
            'corporate_membership_only','corporate_membership_type_id',
            'require_approval','renewal','renewal_period_start', 
            'renewal_period_end', 'expiration_grace_period', 
            'admin_only', 'order',
            'status', 'status_detail')}),
    )
    
    form = MembershipTypeForm
    
    class Media:
        js = ("%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL, 
              "%sjs/membtype.js" % settings.STATIC_URL,)
        
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        # save the expiration method fields
        type_exp_method = form.cleaned_data['type_exp_method']
        type_exp_method_list = type_exp_method.split(",")
        for i, field in enumerate(form.type_exp_method_fields):
            exec('instance.%s="%s"' % (field, type_exp_method_list[i]))
            
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
 
        # save the object
        instance.save()
        #form.save_m2m()
        
        return instance
admin.site.register(MembershipType, MembershipTypeAdmin)