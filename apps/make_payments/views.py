from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from make_payments.forms import MakePaymentForm
from make_payments.utils import make_payment_inv_add
#from site_settings.utils import get_setting


def add(request, form_class=MakePaymentForm, template_name="make_payments/add.html"):
    print  request.COOKIES.get('sessionid','')
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        
        if form.is_valid():
            mp = form.save()
            
            # create invoice
            invoice = make_payment_inv_add(request, mp)
            # updated the invoice_id for mp, so save again
            mp.save()
            
            # email to admin - later
            # email to user - later
            
            # redirect to online payment or confirmation page
            if mp.payment_method == 'cc' or mp.payment_method == 'credit card':
                return HttpResponseRedirect(reverse('payments.views.pay_online', args=[invoice.id, invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('make_payment.add_confirm', args=[mp.id]))
    else:
        form = form_class(request.user)
        #form2 = form_class2()
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
def add_confirm(request, id, template_name="make_payments/add_confirm.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))