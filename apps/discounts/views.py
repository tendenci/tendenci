from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings

from base.http import Http403
from perms.utils import has_perm, update_perms_and_save, is_admin, get_query_filters
from event_logs.models import EventLog
from theme.shortcuts import themed_response as render_to_response
from exports.tasks import TendenciExportTask

from discounts.models import Discount, DiscountUse
from discounts.forms import DiscountForm, DiscountCodeForm

@login_required
def search(request, template_name="discounts/search.html"):
    if not has_perm(request.user, 'discounts.view_discount'):
        raise Http403

    filters = get_query_filters(request.user, 'discounts.view_discount')
    discounts = Discount.objects.filter(filters).distinct()
    query = request.GET.get('q', None)
    if query:
        discounts = discounts.filter(discount_code__icontains=query)

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
            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % discount)
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
            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % discount)
            return redirect('discount.detail', id=discount.id)
    else:
        form = form_class(instance=discount, user=request.user)
        
    return render_to_response(
        template_name,
        {
            'form':form,
            'discount':discount,
        },
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
        
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % discount)
        discount.delete()
        
        return redirect('discounts')

    return render_to_response(template_name, {'discount': discount}, 
        context_instance=RequestContext(request))
    
@csrf_exempt
def discounted_price(request, form_class=DiscountCodeForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            return HttpResponse(json.dumps(
                {
                    "error":False,
                    "price":str(form.new_price()[0]),
                    "discount":str(form.new_price()[1]),
                    "message":"Your discount of $ %s has been added."%str(form.new_price()[1]),
                }), mimetype="text/plain")
        return HttpResponse(json.dumps(
            {
                "error":True,
                "message":"This is not a valid discount code.",
            }), mimetype="text/plain")
    else:
        form = form_class()
    return HttpResponse(
        "<form action='' method='post'>" + form.as_p() + "<input type='submit' value='check'> </form>",
        mimetype="text/html")
        
@login_required
def export(request, template_name="discounts/export.html"):
    """Export Discounts"""
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        # initilize initial values
        file_name = "discounts.xls"
        fields = [
            'discount_code',
            'start_dt',
            'end_dt',
            'never_expires',
            'value',
            'cap',
        ]
        
        if not settings.CELERY_IS_ACTIVE:
            # if celery server is not present 
            # evaluate the result and render the results page
            result = TendenciExportTask()
            response = result.run(Discount, fields, file_name)
            return response
        else:
            result = TendenciExportTask.delay(Discount, fields, file_name)
            return redirect('export.status', result.task_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
