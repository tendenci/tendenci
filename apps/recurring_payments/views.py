from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
#from django.conf import settings
#from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from recurring_payments.models import (RecurringPayment, 
                                       PaymentProfile, 
                                       PaymentTransaction,
                                       RecurringPaymentInvoice)
from recurring_payments.authnet.utils import get_test_mode
from recurring_payments.utils import RecurringPaymentEmailNotices
from recurring_payments.authnet.cim import CIMCustomerProfile

from perms.utils import is_admin
from base.http import Http403
from event_logs.models import EventLog
#from site_settings.utils import get_setting

@login_required
def view_account(request, recurring_payment_id, 
                          template_name="recurring_payments/index.html"):
    """View a recurring payment account.
    """
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)
    
    # only admin or user self can access this page
    if not is_admin(request.user) and request.user.id <> rp.user.id:
        raise Http403
    
    paid_payment_transactions = PaymentTransaction.objects.filter(
                                                recurring_payment=rp,
                                                status=True
                                                                )
    if paid_payment_transactions:
        last_paid_payment_transaction = paid_payment_transactions[0]
    else:
        last_paid_payment_transaction = None
        
    failed_payment_transactions = PaymentTransaction.objects.filter(
                                                recurring_payment=rp,
                                                status=False
                                                                )
    if failed_payment_transactions:
        last_failed_payment_transaction = failed_payment_transactions[0]
    else:
        last_failed_payment_transaction = None
    
    display_failed_transaction = False    
    if last_failed_payment_transaction:
        if not last_paid_payment_transaction or \
            last_failed_payment_transaction.create_dt  \
            > last_paid_payment_transaction.create_dt:
            display_failed_transaction = True
            
    if not rp.trial_amount:
        rp.trial_amount = 0
        
    # rp_invoices
    rp_invoices = RecurringPaymentInvoice.objects.filter(
                                        recurring_payment=rp
                                        ).order_by('-billing_cycle_start_dt')
                                        
    # payment transactions
    payment_transactions = PaymentTransaction.objects.filter(
                                        recurring_payment=rp
                                        ).order_by('-create_dt')
                                        
    # get ready for the add/update payment method button
    test_mode = get_test_mode()
    is_active = (rp.status_detail == 'active')
    if is_active:
        rp.populate_payment_profile()
        payment_profiles = PaymentProfile.objects.filter(
                            customer_profile_id=rp.customer_profile_id, 
                            status=1, status_detail='active')
        if payment_profiles:
            payment_profile = payment_profiles[0]
        else:
            payment_profile = None
            
    else:
        payment_profile = None
    
    
    
    return render_to_response(template_name, {
                                              'rp': rp,
                                              'display_failed_transaction': display_failed_transaction,
                                              'last_paid_payment_transaction': last_paid_payment_transaction,
                                              'last_failed_payment_transaction': last_failed_payment_transaction,
                                              'rp_invoices': rp_invoices,
                                              'payment_transactions': payment_transactions,
                                              'payment_profile': payment_profile,
                                              'test_mode': test_mode,
                                              'is_active': is_active
                                              }, 
        context_instance=RequestContext(request))
    
@staff_member_required
def customers(request, template_name="recurring_payments/customers.html"):
    """Display a list of recurring payment accounts.
    """
    query = request.GET.get('q', None)
    recurring_payments = RecurringPayment.objects.search(query)
    total_customers = RecurringPayment.objects.count()
    # get total amount received
    d = RecurringPaymentInvoice.objects.filter(
                                invoice__balance=0,
                                ).aggregate(total_amount_received=Sum('invoice__total'))
    total_amount_received = d['total_amount_received']
    if not total_amount_received:
        total_amount_received = 0
    # get total amount unpaid
    d = RecurringPaymentInvoice.objects.filter(
                                invoice__balance__gt=0,
                                ).aggregate(total_amount_unpaid=Sum('invoice__balance'))
    total_amount_unpaid = d['total_amount_unpaid']
    if not total_amount_unpaid:
        total_amount_unpaid = 0
    
    # get total amount past due
    d = RecurringPaymentInvoice.objects.filter(
                                invoice__balance__gt=0,
                                billing_dt__lte=datetime.now()
                                ).aggregate(total_amount_past_due=Sum('invoice__balance'))
    total_amount_past_due = d['total_amount_past_due']
    if not total_amount_past_due:
        total_amount_past_due = 0
    
    return render_to_response(template_name, {
                    'recurring_payments': recurring_payments,
                    'total_customers': total_customers,
                    'total_amount_received': total_amount_received,
                    'total_amount_unpaid': total_amount_unpaid,
                    'total_amount_past_due': total_amount_past_due
                                              }, 
        context_instance=RequestContext(request))

  
def transaction_receipt(request, rp_id, payment_transaction_id, rp_guid=None,
                        template_name="recurring_payments/transaction_receipt.html"):
    """Display a transaction receipt.
    """
    if request.user.is_authenticated():
        rp = get_object_or_404(RecurringPayment, pk=rp_id)
        # only admin or user self can access this page
        if not is_admin(request.user) and request.user.id <> rp.user.id:
            raise Http403
    else:
        if not rp_guid: raise Http403
        rp = get_object_or_404(RecurringPayment, pk=rp_id, guid=rp_guid)
    
    payment_transaction = get_object_or_404(PaymentTransaction, 
                                            pk=payment_transaction_id)
    payment_profile = PaymentProfile.objects.filter(
                    payment_profile_id=payment_transaction.payment_profile_id)[0]

    
    return render_to_response(template_name, {
                    'rp': rp,
                    'payment_transaction': payment_transaction,
                    'payment_profile': payment_profile
                                              }, 
        context_instance=RequestContext(request))
    
    
@login_required
def disable_account(request, rp_id, 
                          template_name="recurring_payments/disable.html"):
    """Disable a recurring payment account.
    """
    rp = get_object_or_404(RecurringPayment, pk=rp_id)
    
    # only admin or user self can access this page
    if not is_admin(request.user) and request.user.id <> rp.user.id:
        raise Http403
    if request.method == "POST":
        if request.POST.get('cancel'):
            return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))
        else:
            
            rp.status_detail = 'disabled'
            rp.save()
            
            log_description = '%s disabled' % rp._meta.object_name
            
            # delete the CIM account - only if there is no other rps sharing the same customer profile
            if rp.customer_profile_id:
                
                has_other_rps = RecurringPayment.objects.filter(
                                            customer_profile_id=rp.customer_profile_id
                                            ).exclude(id=rp.id).exists()
                if not has_other_rps:
                    cim_customer_profile = CIMCustomerProfile(rp.customer_profile_id)
                    cim_customer_profile.delete()
                    
                    # delete payment profile belonging to this recurring payment
                    PaymentProfile.objects.filter(customer_profile_id=rp.customer_profile_id).delete()
                    
                    log_description = "%s as well as its CIM account." % log_description
                    
                    rp.customer_profile_id = ''
                    rp.save()
                    
            
            
            # send an email to admin
            rp_email_notice = RecurringPaymentEmailNotices()
            rp_email_notice.email_admins_account_disabled(rp, request.user)
            
            
            # log an event
            log_defaults = {
                        'event_id' : 1120700,
                        'event_data': '%s (%d) disabled by %s' % (rp._meta.object_name, rp.pk, request.user),
                        'description': log_description,
                        'user': request.user,
                        'request': request,
                        'instance': rp,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.INFO, 'Successfully disabled %s' % rp)
                                                                         
            return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))
        
        
    return render_to_response(template_name, {
                    'rp': rp}, 
        context_instance=RequestContext(request))
    
    
    
    
    
    
    
    