from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from haystack.query import SearchQuerySet
from base.http import Http403
import simplejson

from perms.utils import has_perm, get_query_filters
from site_settings.utils import get_setting
from before_and_after.models import BeforeAndAfter, Category, PhotoSet, Subcategory
from event_logs.models import EventLog

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
    
    if get_setting('site', 'global', 'searchindex') and q:
        bnas = BeforeAndAfter.objects.search(query=q, user=request.user)
    else:
        filters = get_query_filters(request.user, 'before_and_after.view_beforeandafter')
        bnas = BeforeAndAfter.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            bnas = bnas.select_related()
    bnas = bnas.order_by('-ordering','-create_dt')
    
    if category:
        category = get_object_or_404(Category, pk=category)
        subcategories = subcategories.filter(category=category.pk)
        bnas = bnas.filter(category=category.pk)
        if subcategory:
            subcategory = get_object_or_404(Subcategory, pk=subcategory)
            bnas = bnas.filter(subcategory=subcategory.pk)
            
    log_defaults = {
        'event_id' : 1090400,
        'event_data': '%s searched by %s' % ('Before and Afters', request.user),
        'description': '%s searched' % 'Before and Afters',
        'user': request.user,
        'request': request,
        'source': 'before_and_afters'
    }
    EventLog.objects.log(**log_defaults)
    
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
    category = bna.category

    if not has_perm(request.user, 'before_and_after.view_beforeandafter', bna):
        raise Http403
    
    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category=category.pk)
    
    log_defaults = {
            'event_id' : 1090500,
            'event_data': '%s (%d) viewed by %s' % (bna._meta.object_name, bna.pk, request.user),
            'description': '%s viewed' % bna._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': bna,
        }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name,
        {
            'categories': categories,
            'subcategories': subcategories,
            'bna': bna,
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
        
