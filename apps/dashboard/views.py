from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def index(request, template_name="dashboard/index.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))
