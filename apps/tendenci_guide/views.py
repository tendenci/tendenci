from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from base.http import Http403
from perms.utils import has_perm
from event_logs.models import EventLog
from perms.utils import is_admin
from tendenci_guide.models import Guide

def guide_page(request, slug=None, template_name="tendenci_guide/detail.html"):
    guide = get_object_or_404(Guide, slug=slug)
    section_guides = Guide.objects.filter(section=guide.section).order_by('ordering')
    remaining = Guide.objects.filter(section=guide.section, ordering__gt=guide.ordering).order_by('ordering')
    if remaining:
        next = remaining[0]
    if is_admin(request.user):
        log_defaults = {
            'event_id' : 1002500,
            'event_data': '%s (%d) viewed by %s' % (guide._meta.object_name, guide.pk, request.user),
            'description': '%s viewed' % guide._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': guide,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, locals(), context_instance=RequestContext(request))
    else:
        raise Http403
