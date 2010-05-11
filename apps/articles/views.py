# django
from django.shortcuts import render_to_response
from django.template import RequestContext

# local
#from articles.models import Article


# Create your views here.
def articles(request, template_name="articles/articles.html"):

    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))