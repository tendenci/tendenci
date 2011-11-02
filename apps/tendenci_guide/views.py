from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404

from base.http import Http403
from perms.utils import has_perm
from event_logs.models import EventLog
from perms.utils import is_admin

def guide_page(request, slug=None, template_name="tendenci_guide/details.html"):
    guides = ['getting-started-with-tendenci',
            'the-dashboard',
            'adding-site-content',
            'home-page-content-and-tags',
            'calendar-events',
            'photo-albums',
            'site-navigation',
            'tips']
    if slug in guides:
        guide_file = "tendenci_guide/%s.html" % slug
        title = slug.replace("-"," ")
        if is_admin(request.user):
#             log_defaults = {
#                 'event_id' : 155000,
#                 'event_data': '%s (%d) viewed by %s' % (quote._meta.object_name, quote.pk, request.user),
#                 'description': '%s viewed' % quote._meta.object_name,
#                 'user': request.user,
#                 'request': request,
#                 'instance': quote,
#             }
#             EventLog.objects.log(**log_defaults)
            return render_to_response(template_name, locals(), context_instance=RequestContext(request))
        else:
            raise Http403
    else:
        raise Http404