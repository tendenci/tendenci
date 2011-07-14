from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from haystack.query import SearchQuerySet
from base.http import Http403
import simplejson

from perms.utils import has_perm
from site_settings.utils import get_setting
from before_and_after.models import BeforeAndAfter, Category, PhotoSet, Subcategory

def subcategories(request):
    cat = request.GET.get('category', None)
    response_dict = [{'id':None, 'label':'Subcategory'}]
    for sub in Subcategory.objects.filter(category=cat):
        response_dict.append({'id':sub.pk, 'label':sub.name})
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

def search(request, template_name='before_and_after/search.html'):
    category = request.GET.get('category', None)
    subcategory = request.GET.get('subcategory', None)
    q = request.GET.get('q', None)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    
    bnas = BeforeAndAfter.objects.search(query=q, user=request.user)
    bnas = bnas.order_by('-create_dt')
    
    if category:
        category = get_object_or_404(Category, pk=category)
        subcategories = subcategories.filter(category=category.pk)
        bnas = bnas.filter(category=category.pk)
        if subcategory:
            subcategory = get_object_or_404(Subcategory, pk=subcategory)
            bnas = bnas.filter(subcategory=subcategory.pk)
    
    return render_to_response(template_name, 
        {
            'categories': categories,
            'subcategories': subcategories,
            'bnas': bnas,
            'category': category,
            'subcategory': subcategory,
            'disclaimer_text': get_setting('module', 'before_and_after', 'searchpagedisclaimertext'),
            'embed_form': get_setting('module', 'before_and_after', 'mainembedform'),
        },
        context_instance=RequestContext(request))

def detail(request, id, template_name='before_and_after/detail.html'):
    bna = get_object_or_404(BeforeAndAfter, id=id)
    
    if not has_perm(request.user, 'before_and_after.view_beforeandafter', bna):
        raise Http403
    
    active = request.GET.get('active', None)
    order = request.GET.get('order', None)
    
    if active:
        try:
            active_photoset = PhotoSet.objects.get(pk=active, before_and_after=bna)
        except:
            active_photoset = bna.featured
    elif order:
        try:
            active_photoset = bna.photoset_set.get(order=order)
        except:
            active_photoset = bna.featured
    else:
        active_photoset = bna.featured
        
    if active_photoset:
        other_photosets = bna.photoset_set.exclude(pk=active_photoset.pk).order_by('order')[0:6]
    else:
        other_photosets = []
    
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    
    return render_to_response(template_name,
        {
            'categories': categories,
            'subcategories': subcategories,
            'bna': bna,
            'active_photoset': active_photoset,
            'other_photosets': other_photosets,
            'embed_form': get_setting('module', 'before_and_after', 'mainembedform'),
            'next': bna.next(request.user),
            'prev': bna.prev(request.user),
        },
        context_instance=RequestContext(request))

def index(request, template_name='before_and_after/index.html'):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    
    return render_to_response(template_name, 
        {
            'categories': categories,
            'subcategories': subcategories,
            'title': get_setting('module', 'before_and_after', 'mainpagetitle'),
            'title_tag': get_setting('module', 'before_and_after', 'mainpagetitletag'),
            'description': get_setting('module', 'before_and_after', 'mainpagedescription'),
            'embed_form': get_setting('module', 'before_and_after', 'mainembedform'),
        },
        context_instance=RequestContext(request))
        
