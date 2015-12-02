from os.path import basename, join, abspath, dirname

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile
from django.core.exceptions import FieldError

from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.files.utils import get_image
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import has_perm
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

    if get_setting('site', 'global', 'searchindex') and query:
        staff = Staff.objects.search(query, user=request.user)
        
    else:
        filters = get_query_filters(request.user, 'staff.view_staff')
        staff = Staff.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            staff = staff.select_related()

    if department and department.isdigit():
        staff = staff.filter(department__id=int(department))

    staff = staff.order_by('-position', 'name', '-status', 'status_detail')

    EventLog.objects.log()

    return render_to_response(template_name, {'staff_members':staff},
        context_instance=RequestContext(request))


@is_enabled('staff')
def search_redirect(request):
    return HttpResponseRedirect(reverse('staff'))
