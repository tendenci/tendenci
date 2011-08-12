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
    
    log_defaults = {
        'event_id' : 1010400,
        'event_data': '%s searched by %s' % ('Discount', request.user),
        'description': '%s searched' % 'Discount',
        'user': request.user,
        'request': request,
        'source': 'discounts'
    }
    EventLog.objects.log(**log_defaults)
    
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
        
    log_defaults = {
        'event_id': 1010500,
        'event_data': '%s (%d) viewed by %s' % (
             discount._meta.object_name,
             discount.pk, request.user
        ),
        'description': '%s viewed' % discount._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': discount,
    }
    EventLog.objects.log(**log_defaults)
    
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
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            discount = form.save(commit=False)
            discount = update_perms_and_save(request, form, discount)
            log_defaults = {
                    'event_id' : 1010100,
                    'event_data': '%s (%d) added by %s' % (discount._meta.object_name, discount.pk, request.user),
                    'description': '%s added' % discount._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': discount,
                }
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.INFO, 'Successfully added %s' % discount)
            return redirect('discount.detail', id=discount.id)
    else:
        form = form_class(user=request.user)
        
    return render_to_response(
        template_name,
        {'form':form},
        context_instance=RequestContext(request),
    )

@login_required
def edit(request, id, form_class=DiscountForm, template_name="discounts/edit.html"):
    discount = get_object_or_404(Discount, id=id)
    if not has_perm(request.user, 'discounts.change_discount', discount):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=discount, user=request.user)
        if form.is_valid():
            discount = form.save(commit=False)
            discount = update_perms_and_save(request, form, discount)
            log_defaults = {
                    'event_id' : 1010200,
                    'event_data': '%s (%d) updated by %s' % (discount._meta.object_name, discount.pk, request.user),
                    'description': '%s updated' % discount._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': discount,
                }
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.INFO, 'Successfully updated %s' % discount)
            return redirect('discount.detail', id=discount.id)
    else:
        form = form_class(instance=discount, user=request.user)
        
    return render_to_response(
        template_name,
        {'form':form},
        context_instance=RequestContext(request),
    )

@login_required
def delete(request, id, template_name="discounts/delete.html"):
    discount = get_object_or_404(Discount, pk=id)

    if not has_perm(request.user,'discounts.delete_discount', discount):
        raise Http403
    
    if request.method == "POST":
        log_defaults = {
            'event_id' : 1010300,
            'event_data': '%s (%d) deleted by %s' % (discount._meta.object_name, discount.pk, request.user),
            'description': '%s deleted' % discount._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': discount,
        }
        EventLog.objects.log(**log_defaults)
        
        messages.add_message(request, messages.INFO, 'Successfully deleted %s' % discount)
        discount.delete()
        
        return redirect('discount.search')

    return render_to_response(template_name, {'discount': discount}, 
        context_instance=RequestContext(request))
