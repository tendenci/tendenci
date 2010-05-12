# django
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# local
from articles.models import Article

def index(request, template_name="articles/index.html"):
    return HttpResponseRedirect(reverse('article.search'))

def search(request, template_name="articles/search.html"):
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))

def view(request, template_name="articles/view.html"):
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))

def print_view(request, template_name="articles/print-view.html"):
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))

def edit(request, template_name="articles/edit.html"):
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))

def delete(request, template_name="articles/delete.html"):
    return render_to_response(template_name, {}, 
        context_instance=RequestContext(request))