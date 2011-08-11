from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages

from base.http import Http403
from perms.utils import has_perm, update_perms_and_save, is_admin
from event_logs.models import EventLog
from discounts.models import Discount, DiscountUse
from discounts.forms import DiscountForm

@login_required
def search(request, template_name="discounts/search.html"):
    query = request.GET.get('q', None)
    discounts = Discount.objects.search(query, user=request.user)
    
    return render_to_response(
        template_name,
        {'discounts':discounts},
        context_instance=RequestContext(request)
    )

@login_required    
def detail(request, id, template_name="discounts/detail.html"):
    discount = get_object_or_404(Discount, id=id)
    
    if not has_perm(request.user, 'discounts.view_discount', discount):
        raise Http403
    
    return render_to_response(
        template_name, 
        {'discount':discount},
        context_instance=RequestContext(request)
    )

@login_required
def add(request, form_class=DiscountForm, template_name="discounts/add.html"):
    if not has_perm(request.user, 'discounts.add_discount'):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            discount = form.save()
            messages.add_message(request, messages.INFO, 'Successfully added %s' % discount)
            return redirect('discount', id=discount.id)
    else:
        form = form_class()
        
    return render_to_response(
        template_name,
        {'form':form},
        context_instance=RequestContext(request),
    )
