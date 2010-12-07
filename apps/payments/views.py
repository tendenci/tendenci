from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from payments.models import Payment
from payments.authorizenet.utils import prepare_authorizenet_sim_form
from invoices.models import Invoice
from base.http import Http403
from base.utils import tcurrency
from event_logs.models import EventLog

from site_settings.utils import get_setting

def pay_online(request, invoice_id, guid="", template_name="payments/pay_online.html"):
    # check if they have the right to view the invoice
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if not invoice.allow_view_by(request.user, guid): raise Http403
    
    # tender the invoice
    if not invoice.is_tendered:
        invoice.tender(request.user)
        # log an event for invoice edit
        log_defaults = {
            'event_id' : 312000,
            'event_data': '%s (%d) edited by %s' % (invoice._meta.object_name, invoice.pk, request.user),
            'description': '%s edited' % invoice._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': invoice,
        }
        EventLog.objects.log(**log_defaults)  
      
    # generate the payment
    payment = Payment()
    
    boo = payment.payments_pop_by_invoice_user(request.user, invoice, guid)
    # log an event for payment add
    log_defaults = {
        'event_id' : 281000,
        'event_data': '%s (%d) added by %s' % (payment._meta.object_name, payment.pk, request.user),
        'description': '%s added' % payment._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': payment,
    }
    EventLog.objects.log(**log_defaults)
    
    # post payment form to gateway and redirect to the vendor so customer can pay from there
    if boo:
        merchant_account = (get_setting("site", "global", "merchantaccount")).lower()
        #merchant_account = "authorizenet"
        if merchant_account == "authorizenet":
            form = prepare_authorizenet_sim_form(request, payment)
            post_url = settings.AUTHNET_POST_URL
        else:   # more vendors 
            form = None
            post_url = ""
    else:
        form = None
        post_url = ""
    return render_to_response(template_name, 
                              {'form':form, 'post_url':post_url}, 
                              context_instance=RequestContext(request))
    
def view(request, id, guid=None, template_name="payments/view.html"):
    payment = get_object_or_404(Payment, pk=id)

    if not payment.allow_view_by(request.user, guid): raise Http403
    payment.amount = tcurrency(payment.amount)
    
    return render_to_response(template_name, {'payment':payment}, 
        context_instance=RequestContext(request))
    
def receipt(request, id, guid, template_name='payments/receipt.html'):
    payment = get_object_or_404(Payment, pk=id)
    if payment.guid <> guid:
        raise Http403
    
    # log an event for payment edit
    if payment:
        if payment.invoice.invoice_object_type == 'job':
            from jobs.models import Job
            try:
                job = Job.objects.get(id=payment.invoice.invoice_object_type_id)
            except Job.DoesNotExist:
                job = None
            return render_to_response(template_name,{'payment':payment, 'job':job}, 
                              context_instance=RequestContext(request))
            
        if payment.invoice.invoice_object_type == 'directory':
            from directories.models import Directory
            try:
                directory = Directory.objects.get(id=payment.invoice.invoice_object_type_id)
            except Directory.DoesNotExist:
                directory = None
            return render_to_response(template_name,{'payment':payment, 'directory':directory}, 
                              context_instance=RequestContext(request))
            
        if payment.invoice.invoice_object_type == 'donation':
            from donations.models import Donation
            try:
                donation = Donation.objects.get(id=payment.invoice.invoice_object_type_id)
            except Donation.DoesNotExist:
                donation = None
            return render_to_response(template_name,{'payment':payment, 'donation':donation}, 
                              context_instance=RequestContext(request))
        
    
    return render_to_response(template_name,{'payment':payment}, 
                              context_instance=RequestContext(request))

        


