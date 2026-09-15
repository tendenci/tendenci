#import os
import json
#from datetime import datetime

from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.shortcuts import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import _does_token_match
import requests
import stripe

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.payments.models import Payment
from .forms import BillingInfoForm, AccountOnBoardingForm
from .utils import (
    build_payment_intent_params,
    configure_stripe,
    payment_update_from_intent,
)
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.recurring_payments.models import RecurringPayment
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.base.utils import get_next_url
from tendenci.apps.event_logs.models import EventLog

from .models import StripeAccount

STRIPE_TOKEN_URL = 'https://connect.stripe.com/oauth/token'
STRIPE_DEAUTHORIZE_URL = 'https://connect.stripe.com/oauth/deauthorize'
REVOKED_STATUS_DETAIL =  'revoked'


def _membership_for_auto_renew(payment):
    """Return membership needing a Stripe RP profile, else None."""
    obj = payment.invoice.get_object()
    if not obj or not hasattr(obj, 'memberships'):
        return None
    memberships = obj.memberships() if callable(obj.memberships) else None
    if not memberships:
        return None
    membership = memberships[0]
    if membership.auto_renew and not membership.has_rp(platform='stripe'):
        return membership
    return None


def _create_payment_intent_for_payment(payment, currency):
    """Create Customer (if auto-renew) and PaymentIntent; return (pi, membership, customer_id)."""
    configure_stripe(stripe)
    membership = _membership_for_auto_renew(payment)
    customer_id = None
    setup_future_usage = None
    if membership and membership.user:
        try:
            customer = stripe.Customer.create(
                email=membership.user.email,
                description='For membership auto renew',
            )
            customer_id = customer.id
            setup_future_usage = 'off_session'
        except Exception:
            customer_id = None
            setup_future_usage = None
            membership = None

    params = build_payment_intent_params(
        payment,
        currency,
        customer_id=customer_id,
        setup_future_usage=setup_future_usage,
    )
    payment_intent = stripe.PaymentIntent.create(**params)
    return payment_intent, membership, customer_id


def _finalize_successful_payment(request, payment, payment_intent):
    """Mark payment approved and create RP when applicable."""
    if payment.is_approved:
        return

    payment_update_from_intent(request, payment_intent, payment)
    payment_processing_object_updates(request, payment)
    log_payment(request, payment)
    send_payment_notice(request, payment)

    customer_id = getattr(payment_intent, 'customer', None)
    if customer_id and not isinstance(customer_id, str):
        customer_id = getattr(customer_id, 'id', None)
    if not customer_id:
        return

    obj = payment.invoice.get_object()
    if not obj or not hasattr(obj, 'memberships'):
        return
    memberships = obj.memberships() if callable(obj.memberships) else None
    if not memberships:
        return
    membership = memberships[0]
    if membership.auto_renew:
        membership.get_or_create_rp(
            request.user,
            platform='stripe',
            customer_profile_id=customer_id,
        )


@login_required
def acct_onboarding(request, template_name='payments/stripe/connect/acct_onboarding.html'):
    # superuser only
    if not request.user.is_superuser:
        raise Http403

    err_msg = ''
    onboarding_form = AccountOnBoardingForm(request.POST or None)
    if request.method == "POST":
        if onboarding_form.is_valid():
            email = onboarding_form.cleaned_data['email']
            account_name = onboarding_form.cleaned_data['account_name']
            scope = onboarding_form.cleaned_data['scope']
            # create a stripe account on stripe
            configure_stripe(stripe)
            try:
                if scope == 'express':
                    acct = stripe.Account.create(
                          type=scope,
                          email=email,
                          capabilities={"card_payments": {"requested": True},
                                        "transfers": {"requested": True}},
                        )
                else: # standard type
                    acct = stripe.Account.create(
                          type=scope,
                          email=email,
                        )
            except stripe.error.InvalidRequestError as e:
                err_msg += str(e)
            except Exception as e:
                err_msg += str(e)

            if not err_msg:
                # save the stripe account to db
                sa = onboarding_form.save(commit=False)
                sa.stripe_user_id = acct.id
                sa.status_detail = 'not completed'
                sa.creator = sa.owner = request.user
                sa.creator_username = sa.owner_username = request.user.username
                sa.save()

                # generate an account link
                # TODO: need to track errors
                site_url = get_setting('site', 'global', 'siteurl')
                acct_link = stripe.AccountLink.create(
                          account=sa.stripe_user_id,
                          refresh_url=site_url+reverse('stripe_connect.acct_onboarding_refresh', args=[sa.id]),
                          return_url=site_url+reverse('stripe_connect.acct_onboarding_done', args=[sa.id]),
                          type="account_onboarding",
                        )

                # redirect user to the account link URL
                return HttpResponseRedirect(acct_link.url)

    if err_msg:
        messages.add_message(request, messages.ERROR, err_msg)

    return render_to_resp(request=request,
                          template_name=template_name,
                        context={'onboarding_form': onboarding_form})


@login_required
def acct_onboarding_refresh(request, sa_id):
    # superuser only
    if not request.user.is_superuser:
        raise Http403

    sa = get_object_or_404(StripeAccount, pk=sa_id)
    site_url = get_setting('site', 'global', 'siteurl')
    err_msg = ''
    if sa.status_detail == 'not completed':
        configure_stripe(stripe)
        try:
            acct_link = stripe.AccountLink.create(
                          account=sa.stripe_user_id,
                          refresh_url=site_url+reverse('stripe_connect.acct_onboarding_refresh', args=[sa.id]),
                          return_url=site_url+reverse('stripe_connect.acct_onboarding_done', args=[sa.id]),
                          type="account_onboarding",
                        )

            # redirect user to the account link URL
            return HttpResponseRedirect(acct_link.url)
        except stripe.error.InvalidRequestError as e:
            err_msg += str(e)
        except Exception as e:
            err_msg += str(e)
    if err_msg:
        messages.add_message(request, messages.ERROR, err_msg)
    return HttpResponseRedirect(reverse('stripe_connect.acct_onboarding_done', args=[sa.id]))


@login_required
def acct_onboarding_done(request, sa_id, template_name='payments/stripe/connect/acct_onboarding_done.html'):
    if not request.user.is_superuser:
        raise Http403

    sa = get_object_or_404(StripeAccount, pk=sa_id)

    # retriever the stripe account
    configure_stripe(stripe)
    acct = stripe.Account.retrieve(sa.stripe_user_id)
    if all([acct.charges_enabled,
            getattr(acct.capabilities, 'card_payments', None) == 'active',
            getattr(acct.capabilities, 'transfers', None) == 'active']):
        # completed
        sa.status_detail = 'active'
        sa.save()
        msg_string = 'Congratulations, your stripe account is set up.'
        messages.add_message(request, messages.SUCCESS, _(msg_string))

    site_url = get_setting('site', 'global', 'siteurl')
    refresh_url= site_url + reverse('stripe_connect.acct_onboarding_refresh', args=[sa.id])
    return render_to_resp(request=request,
                          template_name=template_name,
                        context={'sa': sa,
                                 'refresh_url': refresh_url})


class AuthorizeView(TemplateView):
    template_name = "payments/stripe/connect/authorize.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DeauthorizeView(View):
    template_name = 'payments/stripe/connect/deauthorize.html'

    @method_decorator(login_required)
    def dispatch(self, request, sa_id, *args, **kwargs):
        self.sa = get_object_or_404(StripeAccount, pk=sa_id, status_detail='active')
        if not has_perm(request.user, 'stripe.delete_stripeaccount', self.sa):
            raise Http403
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'sa': self.sa})

    def post(self, request, *args, **kwargs):
        if self.sa.status_detail != REVOKED_STATUS_DETAIL:
            # deauthorize
            r = requests.post(STRIPE_DEAUTHORIZE_URL,
                              data = {'client_secret': settings.STRIPE_SECRET_KEY,
                                      'client_id': get_setting('module', 'payments', 'stripe_connect_client_id'),
                                     'stripe_user_id': self.sa.stripe_user_id,})
            response_json = r.json()
            if r.ok:
                # success
                self.sa.status_detail = REVOKED_STATUS_DETAIL
                self.sa.save()
                msg_string = _('Stripe Connect for "{}" Revoked'.format(self.sa.account_name or self.sa.stripe_user_id))
                messages.add_message(request, messages.SUCCESS, msg_string)
            else:
                # failed
                msg_string = '{} - {}'.format(response_json['error'], response_json['error_description'])
                messages.add_message(request, messages.ERROR, msg_string)

        return HttpResponseRedirect(reverse('stripe_connect.authorize'))


class WebhooksView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = request.body.decode()
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        configure_stripe(stripe)

        # Verify webhook signature and extract the event.
        try:
            event = stripe.Webhook.construct_event(
              payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
         )
        except ValueError as e:
            # Invalid payload
            print(e)
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(e)
            # Invalid signature
            return HttpResponse(status=400)

        # Set status_detail as 'revoked'
        if event.type == 'account.application.deauthorized':
            event_dict = json.loads(payload)
            account = event_dict.get('account', None)
            if account:
                StripeAccount.objects.filter(stripe_user_id=account).update(status_detail=REVOKED_STATUS_DETAIL)
        elif event.type == 'account.updated':
            event_dict = json.loads(payload)
            account = event_dict.get('account', None)
            [sa] = StripeAccount.objects.filter(stripe_user_id=account)[:1] or [None]
            if sa and sa.status_detail == 'not completed':
                acct = stripe.Account.retrieve(account)
                if all([acct.charges_enabled,
                        getattr(acct.capabilities, 'transfers', None) == 'active',
                        getattr(acct.capabilities, 'card_payments', None) == 'active']):
                    # completed
                    sa.status_detail = 'active'
                    sa.save()

        return HttpResponse(status=200)


class FetchAccessToken(View):
    template_name = "payments/stripe/connect/fetch_access_token.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state', None)
        csrf_token = request.META.get("CSRF_COOKIE", None)

        if not code:
            raise Http404
        # if csrf_token doesn't match, raise 403
        if not _does_token_match(state, csrf_token):
            raise Http403

        # fetch access token
        r = requests.post(STRIPE_TOKEN_URL,
                          data = {'client_secret': settings.STRIPE_SECRET_KEY,
                                 'grant_type': 'authorization_code',
                                 'code': code,
                                 'scope': 'read_only'})
        response_json = r.json()
        if r.ok:
            stripe_user_id = response_json['stripe_user_id']
#             livemode = response_json['livemode']
            sa, created = StripeAccount.objects.get_or_create(stripe_user_id=stripe_user_id)
#             if livemode:
#                 sa.livemode_access_token = response_json['access_token']
#                 sa.livemode_stripe_publishable_key = response_json['stripe_publishable_key']
#             else:
#                 sa.testmode_access_token = response_json['access_token']
#                 sa.testmode_stripe_publishable_key = response_json['stripe_publishable_key']
            sa.scope = response_json['scope']
#             sa.token_type = response_json['token_type']
#             sa.refresh_token = response_json['refresh_token']
            if not sa.creator:
                sa.creator = request.user
                sa.creator_username = request.user.username
            sa.owner = request.user
            sa.owner_username = request.user.username
            sa.status_detail='active'
            sa.save()

            # retrieve account info
            configure_stripe(stripe)
            account = stripe.Account.retrieve(stripe_user_id)
            sa.account_name = getattr(account, 'display_name', '') or ''
            if not sa.account_name:
                business_profile = getattr(account, 'business_profile', None)
                if business_profile:
                    sa.account_name = getattr(business_profile, 'name', '') or ''
            sa.email = getattr(account, 'email', '') or ''
            sa.default_currency = getattr(account, 'default_currency', '') or ''
            sa.country = getattr(account, 'country', '') or ''
            sa.save()

            msg_string = _('Success!')
        else:
            sa = None
            msg_string = '{} - {}'.format(response_json['error'], response_json['error_description'])

        return render(request, self.template_name, {'sa': sa, 'msg_string': msg_string})


def pay_online(request, payment_id, guid='', template_name='payments/stripe/payonline.html'):
    if not getattr(settings, 'STRIPE_SECRET_KEY', ''):
        url_setup_guide = 'https://www.tendenci.com/help-files/setting-up-online-payment-processor-and-merchant-provider-on-a-tendenci-site/'
        url_setup_guide = '<a href="{0}">{0}</a>'.format(url_setup_guide)
        merchant_provider = get_setting("site", "global", "merchantaccount")
        msg_string = str(_('ERROR: Online payment has not yet be set up or configured correctly. '))
        if request.user.is_superuser:
            msg_string += str(_('Please follow the guide {0} to complete the setup process for {1}, then try again.').format(url_setup_guide, merchant_provider))
        else:
            msg_string += str(_('Please contact the site administrator to complete the setup process.'))

        messages.add_message(request, messages.ERROR, _(msg_string))

        payment = get_object_or_404(Payment, pk=payment_id, guid=guid)

        return HttpResponseRedirect(reverse('invoice.view', args=[payment.invoice.id]))

    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
    if payment.is_approved:
        return HttpResponseRedirect(reverse('stripe.thank_you', args=[payment.id, payment.guid]))

    currency = get_setting('site', 'global', 'currency') or 'usd'
    billing_info_form = BillingInfoForm(instance=payment)
    client_secret = ''
    err_msg = ''

    try:
        payment_intent, membership, customer_id = _create_payment_intent_for_payment(
            payment, currency)
        client_secret = payment_intent.client_secret
        # save payment_intent_id for later use
        payment.payment_intent_id = payment_intent.id
        payment.save(update_fields=['payment_intent_id'])
    except Exception as e:
        err_msg = str(e)
        messages.add_message(request, messages.ERROR, _(err_msg))

    # Use the request host (not siteurl) so return_url works when browsing
    # via LAN/tunnel hosts that differ from the Site URL setting.
    finalize_url = request.build_absolute_uri(reverse(
        'stripe.finalize', args=[payment.id, payment.guid]))
    save_billing_url = reverse(
        'stripe.save_billing', args=[payment.id, payment.guid])

    connected_account_id = payment.invoice.stripe_connected_account(scope='standard')[0]
    return render_to_resp(
        request=request,
        template_name=template_name,
        context={
            'billing_info_form': billing_info_form,
            'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
            'connected_account_id': connected_account_id,
            'payment': payment,
            'client_secret': client_secret,
            'finalize_url': finalize_url,
            'save_billing_url': save_billing_url,
        },
    )


@require_POST
def save_billing(request, payment_id, guid=''):
    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
    if not payment.payment_intent_id:
        return HttpResponse(
            json.dumps({'ok': False, 'error': 'not allowed'}),
            content_type='application/json',
            status=403,
        )

    if payment.is_approved:
        return HttpResponse(
            json.dumps({'ok': False, 'error': 'already paid'}),
            content_type='application/json',
            status=400,
        )

    billing_info_form = BillingInfoForm(request.POST, instance=payment)
    if not billing_info_form.is_valid():
        errors = {
            field: [str(e) for e in errs]
            for field, errs in billing_info_form.errors.items()
        }
        return HttpResponse(
            json.dumps({'ok': False, 'errors': errors}),
            content_type='application/json',
            status=400,
        )

    billing_info_form.save()
    EventLog.objects.log()
    return HttpResponse(
        json.dumps({'ok': True}),
        content_type='application/json',
    )


def finalize(request, payment_id, guid=''):
    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
    if not payment.payment_intent_id:
        return HttpResponse(
            json.dumps({'ok': False, 'error': 'not allowed'}),
            content_type='application/json',
            status=403,
        )

    payment_intent_id = request.GET.get('payment_intent')
    if not payment_intent_id:
        messages.add_message(
            request, messages.ERROR,
            _('Missing payment confirmation. Please try again.'))
        return HttpResponseRedirect(
            reverse('stripe.payonline', args=[payment.id, payment.guid]))

    if payment_intent_id != payment.payment_intent_id:
        return HttpResponse(
            json.dumps({'ok': False, 'error': 'Payment confirmation mismatch'}),
            content_type='application/json',
            status=400,
        )

    if payment.is_approved:
        return HttpResponseRedirect(
            reverse('stripe.thank_you', args=[payment.id, payment.guid]))

    configure_stripe(stripe)
    try:
        connected_account_id = payment.invoice.stripe_connected_account(scope='standard')[0]
        if connected_account_id:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id,
                                                           stripe_account=connected_account_id)
        else:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))
        return HttpResponseRedirect(
            reverse('stripe.payonline', args=[payment.id, payment.guid]))

    metadata = getattr(payment_intent, 'metadata', None)
    meta_id = getattr(metadata, 'tendenci_payment_id', None) if metadata is not None else None
    meta_guid = getattr(metadata, 'tendenci_payment_guid', None) if metadata is not None else None
    if str(meta_id) != str(payment.id) or str(meta_guid) != str(payment.guid):
        messages.add_message(
            request, messages.ERROR,
            _('Payment confirmation did not match this invoice.'))
        return HttpResponseRedirect(
            reverse('stripe.payonline', args=[payment.id, payment.guid]))

    if getattr(payment_intent, 'status', None) != 'succeeded':
        messages.add_message(
            request, messages.ERROR,
            _('Payment was not completed (status: %s).')
            % payment_intent.status)
        return HttpResponseRedirect(
            reverse('stripe.payonline', args=[payment.id, payment.guid]))

    with transaction.atomic():
        payment = get_object_or_404(
            Payment.objects.select_for_update(), pk=payment_id, guid=guid)
        if not payment.is_approved:
            _finalize_successful_payment(request, payment, payment_intent)

    return HttpResponseRedirect(
        reverse('stripe.thank_you', args=[payment.id, payment.guid]))


@login_required
def update_card(request, rp_id):
    rp = get_object_or_404(RecurringPayment, pk=rp_id, platform='stripe')
    if not has_perm(request.user, 'recurring_payments.change_recurringpayment', rp) \
        and not (rp.user and rp.user.id == request.user.id):
        raise Http403

    configure_stripe(stripe)
    token = request.POST.get('stripeToken')
    try:
        if not rp.customer_profile_id:
            customer = stripe.Customer.create(
                            email=rp.user.email,
                            description=rp.description,
                            source=token)
            rp.customer_profile_id = customer.id
            rp.save()
            msg_string = 'Successfully added payment method'
        else:
            customer = stripe.Customer.retrieve(rp.customer_profile_id)
            customer.source = token
            customer.save()
            msg_string = 'Successfully updated payment method'
        message_status = messages.SUCCESS
    except stripe.error.CardError as e:
        # it's a decline
        json_body = e.json_body
        err  = json_body and json_body['error']
        code = err and err['code']
        message = err and err['message']
        message_status = messages.ERROR
        msg_string = '{message} status={status}, code={code}'.format(
                            message=message, status=e.http_status, code=code)
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        message_status = messages.ERROR
        msg_string = 'Error updating payment method: {}'.format(e)

    messages.add_message(request, message_status, _(msg_string))

    next_page = get_next_url(request)
    if next_page:
        return HttpResponseRedirect(next_page)
    else:
        return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))


def thank_you(request, payment_id, guid='', template_name='payments/receipt.html'):
    #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment':payment})
