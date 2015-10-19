from django.utils.translation import ugettext_lazy as _
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse

from tendenci.apps.base.http import Http403
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import has_perm, update_perms_and_save, get_query_filters
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.theme.shortcuts import themed_response as render_to_response
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.events.models import Registration
from tendenci.apps.memberships.models import MembershipSet
from tendenci.apps.discounts.models import Discount, DiscountUse
from tendenci.apps.discounts.forms import DiscountForm, DiscountCodeForm, DiscountHandlingForm
from tendenci.apps.base.utils import LazyEncoder


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
def detail(request, id, template_name="discounts/view.html"):
    discount = get_object_or_404(Discount, id=id)

    if not has_perm(request.user, 'discounts.view_discount', discount):
        raise Http403

    registrations = Registration.objects.filter(invoice__discount_code=discount.discount_code)
    registrant_list = []
    for registration in registrations:
        registrant_list += registration.registrant_set.filter(discount_amount__gt=0)

    memberships = MembershipSet.objects.filter(invoice__discount_code=discount.discount_code)
    membership_list = []
    for membership in memberships:
        count = DiscountUse.objects.filter(invoice=membership.invoice).count()
        membership_list += membership.membershipdefault_set.all()[:count]

    EventLog.objects.log(instance=discount)

    return render_to_response(
        template_name,
        {'discount':discount,
         'registrant_list':registrant_list,
         'membership_list':membership_list},
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
            messages.add_message(request, messages.SUCCESS, _('Successfully added %(d)s' % {'d': discount}))
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
            messages.add_message(request, messages.SUCCESS, _('Successfully updated %(d)s' % {'d': discount}))
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
        messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(d)s' % {'d' : discount}))
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
                    "message": _("Your discount of $ %(p)s has been added." % {'p': unicode(form.new_price()[1])}),
                }, cls=LazyEncoder), content_type="text/plain")
        return HttpResponse(json.dumps(
            {
                "error": True,
                "message": _("This is not a valid discount code."),
            }, cls=LazyEncoder), content_type="text/plain")
    else:
        form = form_class()
    return HttpResponse(
        "<form action='' method='post'>" + form.as_p() + "<input type='submit' value='check'> </form>",
        content_type="text/html")


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
                    "message": _("A discount of $%(d)s has been added." % { 'd': form.discount.value}),
                }, cls=LazyEncoder), content_type="text/plain")

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
                    "message": _("%(m)sYour discount of $%(dt)s %(dd)s has been added." % {
                        'm' : unicode(msg),
                        'dt' : unicode(discount_total),
                        'dd' : discount_detail }),
                }, cls=LazyEncoder), content_type="text/plain")
        return HttpResponse(json.dumps(
            {
                "error": True,
                "message": _("This is not a valid discount code."),
            }, cls=LazyEncoder), content_type="text/plain")
    else:
        form = form_class()
    return HttpResponse(
        "<form action='' method='post'>" + form.as_p() + "<input type='submit' value='check'> </form>",
        content_type="text/html")

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
