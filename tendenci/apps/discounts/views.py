from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from tendenci.core.base.http import Http403
from tendenci.core.perms.decorators import is_enabled
from tendenci.core.perms.utils import has_perm, update_perms_and_save, get_query_filters
from tendenci.core.event_logs.models import EventLog
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.exports.utils import run_export_task

from tendenci.apps.discounts.models import Discount, DiscountUse
from tendenci.apps.discounts.forms import DiscountForm, DiscountCodeForm, DiscountHandlingForm
from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.redirects.models import Redirect


@is_enabled('discounts')
@login_required
def search(request, template_name="discounts/search.html"):
    if not has_perm(request.user, 'discounts.view_discount'):
        raise Http403

    filters = get_query_filters(request.user, 'discounts.view_discount')
    discounts = Discount.objects.filter(filters).distinct()
    query = request.GET.get('q', None)
    if query:
        discounts = discounts.filter(discount_code__icontains=query)

    EventLog.objects.log()

    return render_to_response(
        template_name,
        {'discounts':discounts},
        context_instance=RequestContext(request)
    )


@is_enabled('discounts')
@login_required    
def detail(request, id, template_name="discounts/detail.html"):
    discount = get_object_or_404(Discount, id=id)
    
    if not has_perm(request.user, 'discounts.view_discount', discount):
        raise Http403

    EventLog.objects.log(instance=discount)

    return render_to_response(
        template_name, 
        {'discount':discount},
        context_instance=RequestContext(request)
    )


@is_enabled('discounts')
@login_required
def add(request, form_class=DiscountForm, template_name="discounts/add.html"):
    if not has_perm(request.user, 'discounts.add_discount'):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            discount = form.save(commit=False)
            discount = update_perms_and_save(request, form, discount)
            form.save_m2m()
            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % discount)
            return redirect('discount.detail', id=discount.id)
    else:
        form = form_class(user=request.user)
        
    return render_to_response(
        template_name,
        {'form':form},
        context_instance=RequestContext(request),
    )


@is_enabled('discounts')
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
            form.save_m2m()
            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % discount)
            return redirect('discount.detail', id=discount.id)
    else:
        form = form_class(instance=discount, user=request.user)

    return render_to_response(
        template_name,
        {
            'form': form,
            'discount': discount,
        },
        context_instance=RequestContext(request),
    )


@is_enabled('discounts')
@login_required
def delete(request, id, template_name="discounts/delete.html"):
    discount = get_object_or_404(Discount, pk=id)

    if not has_perm(request.user, 'discounts.delete_discount', discount):
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % discount)
        discount.delete()

        return redirect('discounts')

    return render_to_response(template_name, {'discount': discount},
        context_instance=RequestContext(request))


@is_enabled('discounts')
@csrf_exempt
def discounted_price(request, form_class=DiscountCodeForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            return HttpResponse(json.dumps(
                {
                    "error": False,
                    "price": unicode(form.new_price()[0]),
                    "discount": unicode(form.new_price()[1]),
                    "message": "Your discount of $ %s has been added." % unicode(form.new_price()[1]),
                }), mimetype="text/plain")
        return HttpResponse(json.dumps(
            {
                "error": True,
                "message": "This is not a valid discount code.",
            }), mimetype="text/plain")
    else:
        form = form_class()
    return HttpResponse(
        "<form action='' method='post'>" + form.as_p() + "<input type='submit' value='check'> </form>",
        mimetype="text/html")


@is_enabled('discounts')
@csrf_exempt
def discounted_prices(request, check=False, form_class=DiscountHandlingForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            if check:
                return HttpResponse(json.dumps(
                {
                    "error": False,
                    "message": "A discount of $%s has been added." % (form.discount.value),
                }), mimetype="text/plain")

            price_list, discount_total, discount_list, msg = form.get_discounted_prices()
            total = sum(price_list)
            new_prices = ';'.join([str(price) for price in price_list])
            if sum(discount_list) > 0:
                discount_detail = '(%s)' % (', '.join(([str(price) for price in discount_list if price >0])))
            else:
                discount_detail = ''
            return HttpResponse(json.dumps(
                {
                    "error": False,
                    "prices": unicode(new_prices),
                    "discount_total": unicode(discount_total),
                    "total": unicode(total),
                    "message": "%sYour discount of $%s %s has been added." % (unicode(msg), unicode(discount_total), 
                                                                               discount_detail),
                }), mimetype="text/plain")
        return HttpResponse(json.dumps(
            {
                "error": True,
                "message": "This is not a valid discount code.",
            }), mimetype="text/plain")
    else:
        form = form_class()
    return HttpResponse(
        "<form action='' method='post'>" + form.as_p() + "<input type='submit' value='check'> </form>",
        mimetype="text/html")

@is_enabled('discounts')
@login_required
def export(request, template_name="discounts/export.html"):
    """Export Discounts"""
    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        fields = [
            'discount_code',
            'start_dt',
            'end_dt',
            'never_expires',
            'value',
            'cap',
        ]
        export_id = run_export_task('discounts', 'discount', fields)
        EventLog.objects.log()
        return redirect('export.status', export_id)

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
