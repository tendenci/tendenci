from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from products.models import Product
from perms.utils import get_notice_recipients, has_perm
from event_logs.models import EventLog

from perms.utils import is_admin

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="products/detail.html"):
    return HttpResponseRedirect(reverse('products.search'))

def detail(request, slug=None, template_name="products/detail.html"):
    if not slug: return HttpResponseRedirect(reverse('products.search'))
    product = get_object_or_404(Product, slug=slug)
    
    if has_perm(request.user, 'product.view_product', product):
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
    query = request.GET.get('q', None)
    products = Product.objects.search(query, user=request.user)
    products = products.order_by('-create_dt')

    log_defaults = {
        'event_id' : 370400,
        'event_data': '%s searched by %s' % ('Product', request.user),
        'description': '%s searched' % 'Product',
        'user': request.user,
        'request': request,
        'source': 'products'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'products':products}, 
        context_instance=RequestContext(request))