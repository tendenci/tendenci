from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404

from haystack.query import SearchQuerySet

from before_and_after.models import BeforeAndAfter, Category

def search(request, template_name='before_and_after/search.html'):
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)
    
    sqs = SearchQuerySet().filter(category=category, subcategory=subcategory)
    
    return render_to_response(template_name, {'sqs': sqs},
        context_instance=RequestContext(request))

def detail(request, id, template_name='before_and_after/detail.html'):
    bna = get_object_or_404(BeforeAndAfter, id=id)
    
    return render_to_response(template_name, {'bna': bna},
        context_instance=RequestContext(request))

def index(request, template_name='before_and_after/index.html'):
    categories = Category.objects.all()
    
    return render_to_response(template_name, {'categories':categories},
        context_instance=RequestContext(request))
