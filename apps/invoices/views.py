from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from invoices.models import Invoice
from site_settings.utils import get_setting
from invoices.utils import invoice_html_display

def view(request, id, guid=None, template_name="invoices/view.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)

    if not invoice.allow_view_by(request.user, guid): return Http403
    
    invoice_display = invoice_html_display(request, invoice)
    notify = request.GET.get('notify', '')
    if guid==None: guid=''
    
    return render_to_response(template_name, {'invoice': invoice,
                                              'guid':guid, 
                                              'notify': notify, 
                                              'invoice_display':invoice_display}, 
        context_instance=RequestContext(request))
    
def search(request, template_name="invoices/search.html"):
    invoices = Invoice.objects.all().order_by('-create_dt')
    return render_to_response(template_name, {'invoices': invoices}, 
        context_instance=RequestContext(request))
