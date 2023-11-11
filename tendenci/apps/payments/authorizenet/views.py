from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.authorizenet.utils import AuthNetAPI
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.site_settings.models import Setting
from tendenci.apps.payments.models import Payment
#from tendenci.apps.payments.authorizenet.utils import get_form_token
from .forms import AcceptJSPaymentForm


def pay_online(request, payment_id, guid='', template_name='payments/authorizenet/payonline.html'):
    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)

    if not getattr(settings, 'MERCHANT_LOGIN', ''):
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

    if payment.is_approved:
        return HttpResponseRedirect(reverse('invoice.view', args=[payment.invoice.id]))

    if 'apitest' in settings.AUTHNET_API_ENDPOINT:
        accept_js_url = 'https://jstest.authorize.net/v3/AcceptUI.js'
    else:
        accept_js_url = 'https://js.authorize.net/v3/AcceptUI.js'

    public_client_key = get_setting('module', 'payments', 'authnetpublicclientkey')
    if not public_client_key:
        anet_api = AuthNetAPI()
        public_client_key = anet_api.get_public_client_key()
        if public_client_key:
            Setting.objects.filter(name='authnetpublicclientkey',
                                   scope='module',
                                   scope_category='payments').update(value=public_client_key)
        else:
            messages.add_message(request, messages.ERROR, _('Error retrieving public client key. Please contact site administrator.'))

    payment_form = AcceptJSPaymentForm(request.POST or None)

    if request.method == "POST" and payment_form.is_valid():
        # handle payment
        anet_api = AuthNetAPI()
        opaque_value = payment_form.cleaned_data['dataValue']
        opaque_descriptor = payment_form.cleaned_data['dataDescriptor']
        payment.first_name = payment_form.cleaned_data['firstName']
        payment.last_name = payment_form.cleaned_data['lastName']
        r = anet_api.create_txn_request(payment, opaque_value, opaque_descriptor)
        if r.ok:
            res_dict = r.json()
            anet_api.process_txn_response(request.user, res_dict, payment)
            if payment.is_approved:
                # for membership auto renew, get customer_profile_id from the transaction
                # and add a recurring payment now
                obj = payment.invoice.get_object()
                if obj and hasattr(obj, 'memberships'):
                    if obj.memberships:
                        membership = obj.memberships()[0]
                        if membership.auto_renew and not membership.has_rp(platform='authorizenet'):
                            kwargs = {'platform': 'authorizenet',}
                            rp = membership.get_or_create_rp(request.user, **kwargs)
                            rp.create_customer_profile_from_trans_id(payment.trans_id)

                # payment is approved, update object
                payment_processing_object_updates(request, payment)

            template_name = 'payments/receipt.html'
            return render_to_resp(request=request, template_name=template_name,
                              context={'payment':payment})
        
    return render_to_resp(request=request, template_name=template_name,
                              context={
                                  'payment': payment,
                                  'payment_form': payment_form,
                                  'accept_js_url': accept_js_url,
                                  'api_login': settings.MERCHANT_LOGIN,
                                  'public_client_key': public_client_key})


# def thank_you(request, payment_id, guid='', template_name='payments/receipt.html'):
#     #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
#     payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
#
#     return render_to_resp(request=request, template_name=template_name,
#                               context={'payment':payment})

# # remove later
# def pay_online_direct(request, payment_id, guid='', template_name='payments/authorizenet/payonline_direct.html'):
#     if not getattr(settings, 'MERCHANT_LOGIN', ''):
#         url_setup_guide = 'https://www.tendenci.com/help-files/setting-up-online-payment-processor-and-merchant-provider-on-a-tendenci-site/'
#         url_setup_guide = '<a href="{0}">{0}</a>'.format(url_setup_guide)
#         merchant_provider = get_setting("site", "global", "merchantaccount")
#         msg_string = str(_('ERROR: Online payment has not yet be set up or configured correctly. '))
#         if request.user.is_superuser:
#             msg_string += str(_('Please follow the guide {0} to complete the setup process for {1}, then try again.').format(url_setup_guide, merchant_provider))
#         else:
#             msg_string += str(_('Please contact the site administrator to complete the setup process.'))
#
#         messages.add_message(request, messages.ERROR, _(msg_string))
#
#         payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
#
#         return HttpResponseRedirect(reverse('invoice.view', args=[payment.invoice.id]))
#
#     payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
#     token =  get_form_token(request, payment)
#     post_url = settings.AUTHNET_POST_URL
#     print('token=', token)
#     return render_to_resp(request=request, template_name=template_name,
#                               context={
#                                   'payment': payment,
#                                   'token': token,
#                                   'post_url': post_url})



# @csrf_exempt
# def sim_thank_you(request, payment_id,
#                   template_name='payments/authorizenet/thankyou.html'):
#     payment = authorizenet_thankyou_processing(
#                                         request,
#                                         request.POST.copy())
#
#     return render_to_resp(request=request, template_name=template_name,
#                               context={'payment': payment})


# @csrf_exempt
# def silent_post(request):
#     # for now, we only handle AUTH_CAPTURE AND AUTH_ONLY
#     if not request.POST.get('x_type', '').lower() in ['auth_capture', 'auth_only']:
#         return HttpResponse('')
#
#     payment = authorizenet_thankyou_processing(
#         request, request.POST.copy())
#
#     log_silent_post(request, payment)
#
#     return HttpResponse('ok')
