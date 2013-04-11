from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from tendenci.core.payments.models import Payment
from tendenci.core.payments.authorizenet.utils import prepare_authorizenet_sim_form
from tendenci.apps.invoices.models import Invoice
from tendenci.core.base.http import Http403
from tendenci.core.event_logs.models import EventLog

from tendenci.core.site_settings.utils import get_setting


def pay_online(request, invoice_id, guid="", template_name="payments/pay_online.html"):
    # check if they have the right to view the invoice
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if not invoice.allow_view_by(request.user, guid):
        raise Http403

    # tender the invoice
    if not invoice.is_tendered:
        invoice.tender(request.user)
        # log an event for invoice edit
        EventLog.objects.log(instance=invoice)

    # generate the payment
    payment = Payment()

    boo = payment.payments_pop_by_invoice_user(request.user, invoice, guid)
    # log an event for payment add
    EventLog.objects.log(instance=payment)

    # post payment form to gateway and redirect to the vendor so customer can pay from there
    if boo:
        merchant_account = (get_setting("site", "global", "merchantaccount")).lower()

        if merchant_account == 'stripe':
            return HttpResponseRedirect(reverse('stripe.payonline', args=[payment.id]))
        else:

            if merchant_account == "authorizenet":
                form = prepare_authorizenet_sim_form(request, payment)
                post_url = settings.AUTHNET_POST_URL
            elif merchant_account == 'firstdata':
                from tendenci.core.payments.firstdata.utils import prepare_firstdata_form
                form = prepare_firstdata_form(request, payment)
                post_url = settings.FIRSTDATA_POST_URL
            elif merchant_account == 'paypalpayflowlink':
                from tendenci.core.payments.payflowlink.utils import prepare_payflowlink_form
                form = prepare_payflowlink_form(request, payment)
                post_url = settings.PAYFLOWLINK_POST_URL
            elif merchant_account == 'paypal':
                from tendenci.core.payments.paypal.utils import prepare_paypal_form
                form = prepare_paypal_form(request, payment)
                post_url = settings.PAYPAL_POST_URL
            else:   # more vendors
                form = None
                post_url = ""
    else:
        form = None
        post_url = ""
    return render_to_response(template_name,
        {'form': form, 'post_url': post_url
        }, context_instance=RequestContext(request))


def view(request, id, guid=None, template_name="payments/view.html"):
    payment = get_object_or_404(Payment, pk=id)

    if not payment.allow_view_by(request.user, guid):
        raise Http403

    return render_to_response(template_name, {'payment': payment},
        context_instance=RequestContext(request))


def receipt(request, id, guid, template_name='payments/receipt.html'):
    payment = get_object_or_404(Payment, pk=id)
    if payment.guid != guid:
        raise Http403

    return render_to_response(template_name, {'payment': payment},
                              context_instance=RequestContext(request))
