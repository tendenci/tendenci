from django.contrib import admin
from django.core.urlresolvers import reverse

from recurring_payments.models import RecurringPayment
from recurring_payments.forms import RecurringPaymentForm
from recurring_payments.authnet.cim import CIMCustomerProfile

from event_logs.models import EventLog

class RecurringPaymentAdmin(admin.ModelAdmin):
    def edit_payment_info_link(self):
        link = reverse('recurring_payment.authnet.update_payment_info', args=[self.id])
        return '<a href="%s">Add/Edit payment info</a>' % (link)
    edit_payment_info_link.allow_tags = True
    
    list_display = ['user', edit_payment_info_link, 'description', 'billing_start_dt',
                     'billing_period', 'billing_frequency', 'payment_amount',  
                     'status_detail']
    list_filter = ['status_detail']
    
    fieldsets = (
        (None, {'fields': ('user', 'description',)}),
        ("Billing Settings", {'fields': ('payment_amount',  
                           'billing_start_dt', 'billing_cycle', 'num_days', )}),
        ("Trial Period", {'fields': ('has_trial_period',  'trial_amount', 
                           'trial_period_start_dt',  'trial_period_end_dt',  ),
                          'description': '*** Note that if the trial period overlaps with ' + \
                          'the initial billing cycle start date, the trial period will end' + \
                          ' on the initial billing cycle start date.'}),
        ('Other Options', {'fields': ('status', 'status_detail',)}),
    )
    
    form = RecurringPaymentForm
    
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        billing_cycle = form.cleaned_data['billing_cycle']
        billing_cycle_list = billing_cycle.split(",")
        instance.billing_frequency = billing_cycle_list[0]
        instance.billing_period = billing_cycle_list[1]
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            
        # save the object
        instance.save()
            
        if not instance.customer_profile_id:
            # create a customer profile on payment gateway
            cp = CIMCustomerProfile()
            d = {'email': instance.user.email,
                 'description': instance.description,
                 'customer_id': str(instance.id)}
            success, response_d = cp.create(**d)
            
            if success:
                instance.customer_profile_id = response_d['customer_profile_id']
               
                instance.save()
        
        return instance
    
    def log_change(self, request, object, message):
        super(RecurringPaymentAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1120200,
            'event_data': '%s for %s(%d) edited by %s' % (object._meta.object_name, 
                                                    object.user, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(RecurringPaymentAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1120100,
            'event_data': '%s for %s(%d) added by %s' % (object._meta.object_name, 
                                                   object.user, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
    
admin.site.register(RecurringPayment, RecurringPaymentAdmin)