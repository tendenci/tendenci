from os.path import basename, join, abspath, dirname

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile

from tendenci.core.base.http import Http403
from tendenci.core.event_logs.models import EventLog
from tendenci.core.files.utils import get_image
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import has_perm
from tendenci.core.perms.utils import get_query_filters, has_view_perm
from tendenci.apps.staff.models import Staff


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

def search(request, template_name="staff/search.html"):
    """Staff plugin search list view"""
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        staff = Staff.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'staff.view_staff')
        staff = Staff.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            staff = staff.select_related()

    staff = staff.order_by('-status','status_detail','start_date')

    EventLog.objects.log()

    return render_to_response(template_name, {'staff_members':staff},
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('staff'))
