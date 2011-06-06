from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404

from before_and_after.models import BeforeAndAfter, Category

def list(request, template_name='before_and_after/list.html'):
    c_name = request.GET.get('category', None)
    s_name = request.GET.get('subcategory', None)
    
    bnas = BeforeAndAfter.objects.all()
    
    if c_name:
        bnas.objects.filter(category__name = c_name)
        if s_name:
            bnas.objects.filter(subcategory__name = s_name)
            
    return render_to_response(template_name, {'bnas': bnas},
        context_instance=RequestContext(request))

def detail(request, id, template_name='before_and_after/detail.html'):
    bna = get_object_or_404(BeforeAndAfter, id=id)
    
    return render_to_response(template_name, {'bna': bna},
        context_instance=RequestContext(request))

def categories(request, template_name='before_and_after/categories.html'):
    categories = Category.objects.all()
    
    return render_to_response(template_name, {'categories':categories},
        context_instance=RequestContext(request))
