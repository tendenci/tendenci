from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from courses.models import Course
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="courses/detail.html"):
    return HttpResponseRedirect(reverse('courses.search'))

def detail(request, pk=None, template_name="courses/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('courses.search'))
    course = get_object_or_404(Course, pk=pk)
    
    if has_perm(request.user, 'course.view_course', course):
        log_defaults = {
            'event_id' : 555500,
            'event_data': '%s (%d) viewed by %s' % (course._meta.object_name, course.pk, request.user),
            'description': '%s viewed' % course._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': course,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'course': course}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="courses/search.html"):
    query = request.GET.get('q', None)
    courses = Course.objects.search(query, user=request.user)
    courses = courses.order_by('-create_dt')

    log_defaults = {
        'event_id' : 555400,
        'event_data': '%s searched by %s' % ('Course', request.user),
        'description': '%s searched' % 'Course',
        'user': request.user,
        'request': request,
        'source': 'courses'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'courses':courses}, 
        context_instance=RequestContext(request))