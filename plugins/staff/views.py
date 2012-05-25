from os.path import basename, join, abspath, dirname

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile

from base.http import Http403
from event_logs.models import EventLog
from files.utils import get_image
from site_settings.utils import get_setting
from perms.utils import has_perm
from perms.utils import is_admin, get_query_filters, has_view_perm


from models import Staff

def details(request, slug=None, cv=None):
    """Staff plugin details view"""
    staff = get_object_or_404(Staff, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (staff.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if cv:
        template_name="staff/cv.html"
    else:
        template_name="staff/view.html"

    if has_view_perm(request.user, 'staff.view_staff', staff):
        log_defaults = {
            'event_id' : 1080500,
            'event_data': '%s (%d) viewed by %s' % (staff._meta.object_name, staff.pk, request.user),
            'description': '%s viewed' % staff._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': staff,
        }
        EventLog.objects.log(**log_defaults)

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
    
    log_defaults = {
        'event_id' : 1080400,
        'event_data': '%s searched by %s' % ('Staff', request.user),
        'description': '%s searched' % 'Staff',
        'user': request.user,
        'request': request,
        'source': 'staff'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'staff_members':staff},
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('staff'))
