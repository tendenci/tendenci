from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from site_settings.models import Setting
from perms.utils import is_admin

@login_required
def index(request, template_name="dashboard/index.html"):
    try:
        profile_redirect = Setting.objects.get(scope = 'site', scope_category = 'global', name = 'profile_redirect')
    except Setting.DoesNotExist:
        profile_redirect = ''
    if profile_redirect and profile_redirect.value != '/dashboard' and not is_admin(request.user):
        return redirect(profile_redirect.value)
    return render_to_response(template_name, context_instance=RequestContext(request))
