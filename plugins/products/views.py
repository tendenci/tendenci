from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from site_settings.utils import get_setting
from products.models import Product
from perms.utils import get_notice_recipients, has_perm, has_view_perm, get_query_filters
from event_logs.models import EventLog

from perms.utils import is_admin
from notification import models as notification


def details(request, slug=None, template_name="products/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('products'))
    product = get_object_or_404(Product, slug=slug)
    
    if has_view_perm(request.user, 'product.view_product', product):
        log_defaults = {
            'event_id' : 370500,
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
    This page lists out all stories from newest to oldest.
    If a search index is available, this page will also
    have the option to search through stories.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        products = Product.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'products.view_story')
        products = Product.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            products = products.select_related()
        products = products.order_by('-create_dt')

    EventLog.objects.log(**{
        'event_id' : 370400,
        'event_data': '%s searched by %s' % ('Product', request.user),
        'description': '%s searched' % 'Product',
        'user': request.user,
        'request': request,
        'source': 'products'
    })

    return render_to_response(template_name, {'products':products}, 
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('products'))

