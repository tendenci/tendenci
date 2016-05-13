from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q

from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import get_query_filters, has_view_perm
from tendenci.apps.staff.models import Staff


@is_enabled('staff')
def detail(request, slug=None, cv=None):
    """Staff plugin details view"""
    staff = get_object_or_404(Staff, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (staff.status_detail).lower() <> 'active' and (not request.user.profile.is_superuser):
        raise Http403

    if cv:
        template_name="staff/cv.html"
    else:
        template_name="staff/view.html"

    if has_view_perm(request.user, 'staff.view_staff', staff):
        EventLog.objects.log(instance=staff)

        return render_to_response(template_name, {'staff': staff},
            context_instance=RequestContext(request))
    else:
        raise Http403


@is_enabled('staff')
def search(request, template_name="staff/search.html"):
    """Staff plugin search list view"""
    query = request.GET.get('q')
    department = request.GET.get('department')

    filters = get_query_filters(request.user, 'staff.view_staff')
    staff = Staff.objects.filter(filters).distinct()
    if not request.user.is_anonymous():
        staff = staff.select_related()

    if query:
        staff = staff.filter(Q(name__icontains=query) | Q(department__name__icontains=query))

    if department and department.isdigit():
        staff = staff.filter(department__id=int(department))

    staff = staff.order_by('-position', 'name', '-status', 'status_detail')

    EventLog.objects.log()

    return render_to_response(template_name, {'staff_members':staff},
        context_instance=RequestContext(request))


@is_enabled('staff')
def search_redirect(request):
    return HttpResponseRedirect(reverse('staff'))
