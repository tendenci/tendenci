import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.translation import ugettext
from django.contrib import messages

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.forms import PaymentSearchForm
from tendenci.apps.payments.models import Payment
from tendenci.apps.payments.authorizenet.utils import prepare_authorizenet_sim_form
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting


logger = logging.getLogger(__name__)


def pay_online(request, invoice_id, guid="", merchant_account=None, template_name="payments/pay_online.html"):
    # check if they have the right to view the invoice
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if not invoice.allow_view_by(request.user, guid):
        raise Http403

    # tender the invoice
    if not invoice.is_tendered:
        invoice.tender(request.user)
        # log an event for invoice edit
        EventLog.objects.log(instance=invoice)

    # For event registration, check if we have enough seats available
    obj = invoice.get_object()
    if obj.__class__.__name__ == 'Registration':
        block_message = ''
        event = obj.event
        spots_available = event.get_spots_status()[1]
        if not spots_available:
            block_message = ugettext('No seats available for this event. Please cancel your registration or contact event organizer.')
        else:
            pricings = {}
            for registrant in obj.registrant_set.filter(cancel_dt__isnull=True):
                pricing = registrant.pricing
                if pricing.registration_cap:
                    if pricing not in pricings:
                        pricings[pricing] = 1
                    else:
                        pricings[pricing] += 1
            for p in pricings:
                price_spots_available = p.spots_available()
                if price_spots_available < pricings[p]:
                    if not price_spots_available:
                        block_message += ugettext('No seats available for price option "{}". '.format(p.title))
                    else:
                        block_message += ugettext('The available seats for price option "{}" is not enough for this registration. '.format(p.title))
            if block_message:
                block_message += ugettext('Please cancel your registration and re-register at a different price.')

        if block_message:
            messages.add_message(request, messages.ERROR, block_message)
            return HttpResponseRedirect(reverse(
                                'event.registration_confirmation',
                                args=(event.id, obj.registrant.hash)))

    # generate the payment
    payment = Payment()

    boo = payment.payments_pop_by_invoice_user(request.user, invoice, guid)
    # log an event for payment add
    EventLog.objects.log(instance=payment)

    # post payment form to gateway and redirect to the vendor so customer can pay from there
    if boo:
        merchant_account = merchant_account or (get_setting("site", "global", "merchantaccount")).lower()

        if merchant_account == 'stripe':
            return HttpResponseRedirect(reverse('stripe.payonline', args=[payment.id, payment.guid]))
        else:

            if merchant_account == "authorizenet":
                form = prepare_authorizenet_sim_form(request, payment)
                post_url = settings.AUTHNET_POST_URL
            elif merchant_account == 'firstdata':
                from tendenci.apps.payments.firstdata.utils import prepare_firstdata_form
                form = prepare_firstdata_form(request, payment)
                post_url = settings.FIRSTDATA_POST_URL
            elif merchant_account == 'firstdatae4':
                from tendenci.apps.payments.firstdatae4.utils import prepare_firstdatae4_form
                form = prepare_firstdatae4_form(request, payment)
                post_url = settings.FIRSTDATAE4_POST_URL
            elif merchant_account == 'paypalpayflowlink':
                from tendenci.apps.payments.payflowlink.utils import prepare_payflowlink_form
                form = prepare_payflowlink_form(request, payment)
                post_url = settings.PAYFLOWLINK_POST_URL
            elif merchant_account == 'paypal':
                from tendenci.apps.payments.paypal.utils import prepare_paypal_form
                form = prepare_paypal_form(request, payment)
                post_url = settings.PAYPAL_POST_URL
            else:   # more vendors
                logger.error(
                    '"{}" did not match a known online payment method. Check the PaymentMethod.machine_name.'.format(
                        merchant_account))
                form = None
                post_url = ""
    else:
        form = None
        post_url = ""
    return render_to_resp(request=request, template_name=template_name, context={'form': form, 'post_url': post_url
        })

@login_required
def view(request, id, guid=None, template_name="payments/view.html"):
    payment = get_object_or_404(Payment, pk=id)

    if not payment.allow_view_by(request.user, guid):
        raise Http403

    return render_to_resp(request=request, template_name=template_name,
        context={'payment': payment})


def receipt(request, id, guid, template_name='payments/receipt.html'):
    payment = get_object_or_404(Payment, pk=id)
    if payment.guid != guid:
        raise Http403

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment': payment})


@login_required
def search(request, template_name='payments/search.html'):
    search_criteria = None
    search_text = None
    search_method = None

    form = PaymentSearchForm(request.GET)
    if form.is_valid():
        search_criteria = form.cleaned_data.get('search_criteria')
        search_text = form.cleaned_data.get('search_text')
        search_method = form.cleaned_data.get('search_method')

    payments = Payment.objects.all()
    if search_criteria and search_text:
        search_type = '__iexact'
        if search_method == 'starts_with':
            search_type = '__istartswith'
        elif search_method == 'contains':
            search_type = '__icontains'
        search_filter = {'%s%s' % (search_criteria,
                                   search_type): search_text}
        payments = payments.filter(**search_filter)

    if request.user.profile.is_superuser:
        payments = payments.order_by('-create_dt')
    else:
        from django.db.models import Q
        payments = payments.filter(Q(creator=request.user) | Q(owner=request.user)).order_by('-create_dt')

    return render_to_resp(request=request, template_name=template_name,
                              context={'payments': payments, 'form': form})
