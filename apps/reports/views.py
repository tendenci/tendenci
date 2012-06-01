# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from base.http import Http403

@login_required
def index(request, template_name="reports/index.html"):

    if not request.user.profile.is_superuser:
        raise Http403

    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))