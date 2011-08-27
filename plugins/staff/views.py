from os.path import basename, join, abspath, dirname

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile

from base.http import Http403
from event_logs.models import EventLog
from files.utils import get_image
from perms.utils import has_perm
from perms.utils import is_admin


from models import Staff

def index(request, slug=None, cv=None):
    if not slug: return HttpResponseRedirect(reverse('staff.search'))
    staff = get_object_or_404(Staff, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (staff.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if cv:
        template_name="staff/cv.html"
    else:
        template_name="staff/view.html"
        
    log_defaults = {
        'event_id' : 1080500,
        'event_data': '%s (%d) viewed by %s' % (staff._meta.object_name, staff.pk, request.user),
        'description': '%s viewed' % staff._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': staff,
    }
    EventLog.objects.log(**log_defaults)
    
    if has_perm(request.user, 'staff.view_staff', staff):
        return render_to_response(template_name, {'staff': staff},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="staff/search.html"):
    query = request.GET.get('q', None)
    staff = Staff.objects.search(query, user=request.user)
    staff = staff.order_by('start_date')
    
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
