from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse 
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.template import Template

from base.http import Http403
from perms.utils import has_perm, is_admin
from event_logs.models import EventLog
from wp_exporter.utils import gen_xml

def index(request, template_name="wp_exporter/index.html"):
    if not is_admin(request.user):
        raise Http403
    
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))

def download(request, template_name="wp_importer/detail.html"):
    if not is_admin(request.user):
        raise Http403
        
    xml = gen_xml()
    
    response = HttpResponse(xml.content, mimetype='text/xml')
    response['Content-Disposition'] = 'attachment; filename=export.xml'
    return response
