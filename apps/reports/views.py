# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from base.http import Http403
from perms.utils import is_admin, is_developer

@login_required
def index(request, template_name="reports/index.html"):

    if not is_admin(request.user) and is_developer(request.user):
        raise Http403

    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))