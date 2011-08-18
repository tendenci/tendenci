from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from recurring_payments.models import RecurringPayment, PaymentProfile
from recurring_payments.authnet.cim import CustomerProfile, CustomerPaymentProfile, HostedProfilePage

@staff_member_required
def manage_payment_info(request, recurring_payment_id, 
                          template_name="recurring_payments/authnet/cim_manage_payment_info.html"):
    """
    Add or edit payment info.
    """
    if hasattr(settings, 'AUTHNET_CIM_TEST_MODE') and  settings.AUTHNET_CIM_TEST_MODE:
        test_mode = 'true'
        form_post_url = "https://test.authorize.net/profile/manage"
    else:
        test_mode = 'false'
        form_post_url = "https://secure.authorize.net/profile/manage"
    rp = get_object_or_404(RecurringPayment, pk=recurring_payment_id)
    payment_profiles = PaymentProfile.objects.filter(recurring_payment=rp, status=1, status_detail='active')
    
    # get the token from payment gateway for this customer (customer_profile_id=4356210)
    hpp = HostedProfilePage(rp.customer_profile_id)
    response_d = hpp.get()
    
    token = response_d['token']
    
    template_name = "recurring_payments/authnet/cim_manage_payment_iframe.html"
    
    return render_to_response(template_name, {'token': token, 'test_mode': test_mode, 
                                              'form_post_url': form_post_url,
                                              'payment_profiles': payment_profiles}, 
        context_instance=RequestContext(request))