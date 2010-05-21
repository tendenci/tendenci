from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext

from site_settings.models import Setting
from site_settings.forms import build_settings_form

# temporary
import logging

def index(request, scope, scope_category, template_name="site_settings/settings.html"):
    settings = Setting.objects.filter(scope=scope, scope_category=scope_category)
    if not settings:
        raise Http404
    
    if request.method == 'POST':
        form = build_settings_form(settings)(request.POST)
        if form.is_valid():
            logging.debug(dir(form))
            logging.debug(form.fields)
            logging.debug(form.cleaned_data)
    else:
        form = build_settings_form(settings)()
        
    return render_to_response(template_name, {'form': form }, context_instance=RequestContext(request))