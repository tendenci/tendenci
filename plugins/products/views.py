from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from products.models import Product
from products.forms import ProductSearchForm
from perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters, has_view_perm
from site_settings.utils import get_setting
from event_logs.models import EventLog

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="products/detail.html"):
    return HttpResponseRedirect(reverse('products.search'))

def detail(request, slug=None, template_name="products/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('products.search'))
    product = get_object_or_404(Product, product_slug=slug)
    
    if has_perm(request.user, 'product.view_product', product):
        log_defaults = {
            'event_id' : 1150500,
            'event_data': '%s (%d) viewed by %s' % (product._meta.object_name, product.pk, request.user),
            'description': '%s viewed' % product._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': product,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'product': product}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="products/search.html"):
    """
    Searches products according to the query string, category
    dropdown and formulation dropdown.
    """
    form = ProductSearchForm(request.GET)
    if form.is_valid():
		query = form.cleaned_data['q']
		category = form.cleaned_data['category']
		formulation = form.cleaned_data['formulation']
    
    if get_setting('site', 'global', 'searchindex') and query:
        products = Product.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'product.view_product')
        products = Product.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            products = products.select_related()
            
    if category:
        products = products.filter(category=category)
    if formulation:
		products = products.filter(formulation=formulation)

    products = products.order_by('-create_dt')

    log_defaults = {
        'event_id' : 1150400,
        'event_data': '%s searched by %s' % ('Product', request.user),
        'description': '%s searched' % 'Product',
        'user': request.user,
        'request': request,
        'source': 'products'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'products':products, 'form':form}, 
        context_instance=RequestContext(request))
