from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404

from tendenci.core.base.http import Http403
from tendenci.core.perms.utils import has_perm
from tendenci.core.event_logs.models import EventLog
from tendenci.addons.tendenci_guide.models import Guide

def guide_page(request, slug=None, template_name="tendenci_guide/detail.html"):
    guide = get_object_or_404(Guide, slug=slug)
    section_guides = Guide.objects.filter(section=guide.section).order_by('position')
    remaining = Guide.objects.filter(section=guide.section, position__gt=guide.position).order_by('position')
    if remaining:
        next = remaining[0]
    if request.user.profile.is_superuser:

        EventLog.objects.log(instance=guide)
        return render_to_response(template_name, locals(), context_instance=RequestContext(request))
    else:
        raise Http403
