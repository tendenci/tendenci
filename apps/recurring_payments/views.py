from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from recurring_payments.models import (RecurringPayment, 
                                       PaymentProfile, 
                                       PaymentTransaction,
                                       RecurringPaymentInvoice)

from perms.utils import has_perm, is_admin
from base.http import Http403
from site_settings.utils import get_setting

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
    
    return render_to_response(template_name, {
                                              'rp': rp,
                                              'display_failed_transaction': display_failed_transaction,
                                              'last_paid_payment_transaction': last_paid_payment_transaction,
                                              'last_failed_payment_transaction': last_failed_payment_transaction,
                                              'rp_invoices': rp_invoices,
                                              'payment_transactions': payment_transactions
                                              }, 
        context_instance=RequestContext(request))