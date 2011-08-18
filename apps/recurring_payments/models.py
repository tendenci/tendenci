import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType


class RecurringPayment(models.Model):
    guid = models.CharField(max_length=50)
    # gateway assigned ID associated with the customer profile
    customer_profile_id = models.CharField(max_length=100, default='')
    user = models.ForeignKey(User, related_name="recurring_payment_user",  null=True)
    # with object_content_type and object_content_id, we can apply the recurring 
    # payment to other modules such as memberships, jobs, etc.
    object_content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_content_id = models.IntegerField(default=0, blank=True, null=True)

    billing_period = models.CharField(max_length=50, choices=(('month', _('Month')),
                                                            ('year', _('Year')),
                                                            ('week', _('Week')),
                                                            ('day', _('Day')),
                                                            ))
    billing_frequency = models.IntegerField(default=1)
    billing_cycle_start_dt = models.DateTimeField()
    billing_cycle_end_dt = models.DateTimeField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    has_trial_period = models.BooleanField(default=0)
    trial_period_start_dt = models.DateTimeField(blank=True, null=True)
    trial_period_end_dt = models.DateTimeField(blank=True, null=True)
    trial_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    next_billing_dt = models.DateTimeField(blank=True, null=True)
    last_payment_received_dt = models.DateTimeField(blank=True, null=True)
    num_billing_cycle_completed = models.IntegerField(default=0, blank=True, null=True)
    num_billing_cycle_failed = models.IntegerField(default=0, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2)
    

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="recurring_payment_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="recurring_payment_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='active')
    status = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(RecurringPayment, self).save(*args, **kwargs)

class PaymentProfile(models.Model):
    recurring_payment =  models.ForeignKey(RecurringPayment)
    # assigned by gateway
    payment_profile_id = models.CharField(max_length=100, default='')
    card_type = models.CharField(max_length=50, null=True)
    # last 4 digits of card number
    card_num = models.CharField(max_length=4, null=True)
    expiration_dt = models.DateTimeField(blank=True, null=True)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="payment_profile_creator",  null=True)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="payment_profile_owner", null=True)
    owner_username = models.CharField(max_length=50, null=True)
    status_detail = models.CharField(max_length=50, default='active')
    status = models.BooleanField(default=True)


class PaymentTransaction(models.Model):
    payment_profile =  models.ForeignKey(PaymentProfile)
    # trans_type - capture, refund or void
    trans_type  = models.CharField(max_length=50, null=True) 
    # refid       
    paymentid =  models.IntegerField()       
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name="payment_transaction_creator",  null=True)

    status_detail = models.CharField(max_length=50,  null=True)