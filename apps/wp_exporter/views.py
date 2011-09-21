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
from wp_exporter.forms import ExportForm

def index(request, form_class=ExportForm ,template_name="wp_exporter/index.html"):
    if not is_admin(request.user):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            xml = gen_xml(form.cleaned_data)
            response = HttpResponse(xml.content, mimetype='text/xml')
            response['Content-Disposition'] = 'attachment; filename=export.xml'
            return response
    else:
        form = form_class()
    
    return render_to_response(template_name, {
        'form':form,
    },context_instance=RequestContext(request))

