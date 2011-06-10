from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404

from haystack.query import SearchQuerySet

from before_and_after.models import BeforeAndAfter, Category, PhotoSet, Subcategory

def search(request, template_name='before_and_after/search.html'):
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)
    q = request.GET.get('q', None)
    
    bnas = BeforeAndAfter.objects.search(query=q, user=request.user)
    
    if category:
        category = get_object_or_404(Category, pk=category)
        bnas = bnas.filter(category=category.pk)
        if subcategory:
            subcategory = get_object_or_404(Subcategory, pk=subcategory)
            bnas = bnas.filter(subcategory=subcategory.pk)
    
    return render_to_response(template_name, 
        {
            'bnas': bnas,
            'category': category,
            'subcategory': subcategory,
        },
        context_instance=RequestContext(request))

def detail(request, id, template_name='before_and_after/detail.html'):
    bna = get_object_or_404(BeforeAndAfter, id=id)
    
    active = request.GET.get('active', None)
    
    if active:
        active_photoset = get_object_or_404(PhotoSet, pk=active, before_and_after=bna)
    else:
        active_photoset = bna.featured
        
    if active_photoset:       
        other_photosets = bna.photoset_set.exclude(pk=active_photoset.pk)[0:6]
    else:
        other_photosets = []
    
    return render_to_response(template_name,
        {
            'bna': bna,
            'active_photoset': active_photoset,
            'other_photosets': other_photosets,
        },
        context_instance=RequestContext(request))

def index(request, template_name='before_and_after/index.html'):
    categories = Category.objects.all()
    
    return render_to_response(template_name, {'categories':categories},
        context_instance=RequestContext(request))
