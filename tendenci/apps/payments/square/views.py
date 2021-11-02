#import os
import math
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
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.shortcuts import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import _compare_salted_tokens
import requests
import stripe

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.payments.models import Payment
from .forms import StripeCardForm, BillingInfoForm
from .utils import payment_update_stripe
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.recurring_payments.models import RecurringPayment
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm

from .models import StripeAccount
from .utils import stripe_set_app_info

STRIPE_TOKEN_URL = 'https://connect.stripe.com/oauth/token'
STRIPE_DEAUTHORIZE_URL = 'https://connect.stripe.com/oauth/deauthorize'
REVOKED_STATUS_DETAIL =  'revoked'


class AuthorizeView(TemplateView):
    template_name = "payments/stripe/connect/authorize.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuthorizeView, self).dispatch(*args, **kwargs)


class DeauthorizeView(View):
    template_name = 'payments/stripe/connect/deauthorize.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, sa_id, *args, **kwargs):
        self.sa = get_object_or_404(StripeAccount, pk=sa_id, status_detail='active')
        if not has_perm(request.user, 'stripe.delete_stripeaccount', self.sa):
            raise Http403
        return super(DeauthorizeView, self).dispatch(request, *args, **kwargs)
    
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
                msg_string = '{0} - {1}'.format(response_json['error'], response_json['error_description'])
                messages.add_message(request, messages.ERROR, msg_string)

        return HttpResponseRedirect(reverse('stripe_connect.authorize'))

class WebhooksView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super(WebhooksView, self).dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        payload = request.body.decode()
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        stripe_set_app_info(stripe)

        try:
            event = stripe.Webhook.construct_event(
              payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
         )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Set status_detail as 'revoked'
        if event.type == 'account.application.deauthorized':
            event_dict = json.loads(payload)
            account = event_dict.get('account', None)
            if account:
                StripeAccount.objects.filter(stripe_user_id=account).update(status_detail=REVOKED_STATUS_DETAIL)

        return HttpResponse(status=200)


class FetchAccessToken(View):
    template_name = "payments/stripe/connect/fetch_access_token.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FetchAccessToken, self).dispatch(*args, **kwargs)

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state', None)
        csrf_token = request.META.get("CSRF_COOKIE", None)

        if not code:
            raise Http404
        # if csrf_token doesn't match, raise 403
        if not _compare_salted_tokens(state, csrf_token):
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
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.api_version = settings.STRIPE_API_VERSION
            stripe_set_app_info(stripe)
            account = stripe.Account.retrieve(stripe_user_id)
            sa.account_name = account.get('display_name', '')
            sa.email = account.get('email', '')
            sa.default_currency = account.get('default_currency', '')
            sa.country = account.get('country', '')
            sa.save()
        
            msg_string = _('Success!')
        else:
            sa = None
            msg_string = '{0} - {1}'.format(response_json['error'], response_json['error_description'])

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
            
    with transaction.atomic():
        payment = get_object_or_404(Payment.objects.select_for_update(), pk=payment_id, guid=guid)
        form = StripeCardForm(request.POST or None)
        billing_info_form = BillingInfoForm(request.POST or None, instance=payment)
        currency = get_setting('site', 'global', 'currency')
        if not currency:
            currency = 'usd'
        if request.method == "POST" and form.is_valid():
            # get stripe token and make a payment immediately
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            stripe.api_version = settings.STRIPE_API_VERSION
            stripe_set_app_info(stripe)
            token = request.POST.get('stripe_token')

            if billing_info_form.is_valid():
                payment = billing_info_form.save()

            # determine if we need to create a stripe customer (for membership auto renew)
            customer = False
            obj_user = None
            membership = None
            obj = payment.invoice.get_object()
            if obj and hasattr(obj, 'memberships'):
                if obj.memberships:
                    membership = obj.memberships()[0]
                    if membership.auto_renew and not membership.has_rp(platform='stripe'):
                        obj_user = membership.user
                    else:
                        membership = None

            if obj_user:
                try:
                    # Create a Customer:
                    customer = stripe.Customer.create(
                                email=obj_user.email,
                                description="For membership auto renew",
                                source=token,
                    )
                except:
                    customer = None

            # create the charge on Stripe's servers - this will charge the user's card
            params = {
                       'amount': math.trunc(payment.amount * 100), # amount in cents, again
                       'currency': currency,
                       'description': payment.description
                      }
            if customer:
                params.update({'customer': customer.id})
            else:
                params.update({'card': token})

            try:
                charge_response = stripe.Charge.create(**params)
                # an example of response: https://api.stripe.com/v1/charges/ch_YjKFjLIItzRDv7
                #charge_response = simplejson.loads(charge)
            except (stripe.error.CardError, stripe.error.InvalidRequestError) as e:
                # it's a decline
                json_body = e.json_body
                err  = json_body and json_body['error']
                code = err and err['code']
                message = err and err['message']
                charge_response = '{message} status={status}, code={code}'.format(
                            message=message, status=e.http_status, code=code)
                
            except Exception as e:
                if hasattr(e, 'message'):
                    charge_response = e.message
                else:
                    charge_response = str(e)

            # add a rp entry now
            if hasattr(charge_response,'paid') and charge_response.paid:
                if customer and membership:
                    kwargs = {'platform': 'stripe',
                              'customer_profile_id': customer.id,
                              }
                    membership.get_or_create_rp(request.user, **kwargs)

            # update payment status and object
            if not payment.is_approved:  # if not already processed
                payment_update_stripe(request, charge_response, payment)
                payment_processing_object_updates(request, payment)

                # log an event
                log_payment(request, payment)

                # send payment recipients notification
                send_payment_notice(request, payment)

            # redirect to thankyou
            return HttpResponseRedirect(reverse('stripe.thank_you', args=[payment.id, payment.guid]))

    return render_to_resp(request=request, template_name=template_name,
                              context={'form': form,
                                              'billing_info_form': billing_info_form,
                                              'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
                                              'payment': payment})


@login_required
def update_card(request, rp_id):
    rp = get_object_or_404(RecurringPayment, pk=rp_id, platform='stripe')
    if not has_perm(request.user, 'recurring_payments.change_recurringpayment', rp) \
        and not (rp.user and rp.user.id == request.user.id):
        raise Http403

    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    stripe.api_version = settings.STRIPE_API_VERSION
    stripe_set_app_info(stripe)
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
    next_page = request.GET.get('next')
    if next_page:
        return HttpResponseRedirect(next_page)
    else:
        return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))


def thank_you(request, payment_id, guid='', template_name='payments/receipt.html'):
    #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment':payment})
