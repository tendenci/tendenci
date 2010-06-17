from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from make_payments.forms import MakePaymentForm
from make_payments.utils import make_payment_inv_add


def add(request, form_class=MakePaymentForm, template_name="make_payments/add.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        
        if form.is_valid():
            mp = form.save(commit=False)
            
            # create invoice
            invoice = make_payment_inv_add(request.user, mp)
            mp.save()
            
            # email to admin - later
            # email to user - later
            
            # redirect to online payment or confirmation page
            if mp.payment_method == 'cc' or mp.payment_method == 'credit card':
                return HttpResponseRedirect(reverse('payments.pay_online', args=[invoice.id, invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('make_payment.addconf', args=[mp.id]))
    else:
        form = form_class(request.user)
        #form2 = form_class2()
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))