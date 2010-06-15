import uuid
#guid = str(uuid.uuid4()))
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from make_payments.forms import MakePaymentForm


def add(request, form_class=MakePaymentForm, template_name="make_payments/add.html"):
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        
        if form.is_valid():
            mp = form.save(commit=False)
            
            # create invoice
                
            mp.save()
            # email to admin
            # email to user
            # redirect to online payment or confirmation page
            
            return HttpResponseRedirect(reverse('make_payment.addconf', args=[mp.id]))
    else:
        form = form_class(request.user)
        #form2 = form_class2()
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))