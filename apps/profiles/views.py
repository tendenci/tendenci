# django
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.
def profiles(request, template_name="profiles/profiles.html"):
    return render_to_response(template_name, {}, 
                              context_instance=RequestContext(request))
