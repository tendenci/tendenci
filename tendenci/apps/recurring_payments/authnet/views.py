from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
#from django.core.urlresolvers import reverse
from django.http import HttpResponse
#from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

from tendenci.addons.recurring_payments.models import RecurringPayment, PaymentProfile
from tendenci.addons.recurring_payments.authnet.cim import CIMCustomerProfile, CIMHostedProfilePage
from tendenci.addons.recurring_payments.authnet.utils import get_token, get_test_mode

from tendenci.core.base.http import Http403
#from tendenci.core.site_settings.utils import get_setting
from tendenci.core.base.decorators import ssl_required

@login_required
def manage_payment_info(request, recurring_payment_id,
                          template_name="recurring_payments/authnet/cim_manage_payment_iframe2.html"):
    """
    Add or edit payment info.
    """
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)
    gateway_error = False

    # only admin or user self can access this page
    if not request.user.profile.is_superuser and request.user.id <> rp.user.id:
        raise Http403

    if hasattr(settings, 'AUTHNET_CIM_TEST_MODE') and  settings.AUTHNET_CIM_TEST_MODE:
        test_mode = 'true'
        form_post_url = "https://test.authorize.net/profile/manage"
    else:
        test_mode = 'false'
        form_post_url = "https://secure.authorize.net/profile/manage"

    if not rp.customer_profile_id:
        # customer_profile is not available yet for this customer, create one now
        cp = CIMCustomerProfile()
        d = {'email': rp.user.email,
             'description': rp.description,
             'customer_id': str(rp.id)}
        success, response_d = cp.create(**d)
        if success:
            rp.customer_profile_id = response_d['customer_profile_id']
            rp.save()
        else:
            gateway_error = True


    #payment_profiles = PaymentProfile.objects.filter(recurring_payment=rp, status=1, status_detail='active')

    # get the token from payment gateway for this customer (customer_profile_id=4356210)
    token = ""
    if not gateway_error:
        hosted_profile_page = CIMHostedProfilePage(rp.customer_profile_id)
        success, response_d = hosted_profile_page.get()

        if not success:
            gateway_error = True
        else:
            token = response_d['token']

    return render_to_response(template_name, {'token': token,
                                              'test_mode': test_mode,
                                              'form_post_url': form_post_url,
                                              'rp': rp,
                                              'gateway_error': gateway_error
                                              },
        context_instance=RequestContext(request))


@ssl_required
@login_required
def update_payment_info(request, recurring_payment_id,
                          template_name="recurring_payments/authnet/cim_update_payment_info2.html"):
    """
    Add or edit payment info.
    """
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)

    # only admin or user self can access this page
    if not request.user.profile.is_superuser and request.user.id <> rp.user.id:
        raise Http403

    rp.populate_payment_profile()

    payment_profiles = PaymentProfile.objects.filter(
                                        customer_profile_id=rp.customer_profile_id,
                                        status=True, status_detail='active')
    if payment_profiles:
        payment_profile = payment_profiles[0]
    else:
        payment_profile = None


    token, gateway_error = get_token(rp, CIMCustomerProfile, CIMHostedProfilePage,
                                     is_secure=request.is_secure())
    test_mode = get_test_mode()


    return render_to_response(template_name, {'rp': rp,
                                              'payment_profile': payment_profile,
                                              'token': token,
                                              'test_mode': test_mode,
                                              'gateway_error': gateway_error
                                              },
        context_instance=RequestContext(request))


@login_required
def update_payment_profile_local(request):
    """
    Update the local payment profile entry.
    """
    recurring_payment_id = request.POST.get('rpid')
    payment_profile_id = request.POST.get('ppid')
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)

    # only admin or user self can access this page
    if not request.user.profile.is_superuser and request.user.id <> rp.user.id:
        raise Http403

    ret_d = {}
    valid_cpp_ids, invalid_cpp_ids = rp.populate_payment_profile(validation_mode='liveMode')
    if valid_cpp_ids:
        if payment_profile_id in valid_cpp_ids:
            ret_d['valid_cpp_id'] = payment_profile_id
        else:
            ret_d['valid_cpp_id'] = valid_cpp_ids[0]
    if invalid_cpp_ids:
        if payment_profile_id in invalid_cpp_ids:
            ret_d['invalid_cpp_id'] = payment_profile_id
        else:
            ret_d['invalid_cpp_id'] = invalid_cpp_ids[0]

    # just so the owner and update_dt are updated
    try:
        payment_profile = PaymentProfile.objects.get(
                                id=payment_profile_id
                                ).save()
    except: pass

    return HttpResponse(simplejson.dumps(ret_d))


def retrieve_token(request):
    """
    retrieve a token for a given recurring payment.
    """
    recurring_payment_id = request.POST.get('rpid')
    guid = request.POST.get('guid')
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)
    if guid != rp.guid:
        raise Http403

    token, gateway_error = get_token(rp,
                                     CIMCustomerProfile,
                                     CIMHostedProfilePage,
                                     is_secure=request.is_secure())

    return HttpResponse(token)
