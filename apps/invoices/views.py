from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from base.http import Http403
from invoices.models import Invoice
from invoices.forms import AdminNotesForm, AdminAdjustForm
from invoices.utils import invoice_html_display
from perms.utils import is_admin

def view(request, id, guid=None, form_class=AdminNotesForm, template_name="invoices/view.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)

    if not invoice.allow_view_by(request.user, guid): return Http403
    
    if is_admin(request.user):
        if request.method == "POST":
            form = form_class(request.POST, instance=invoice)
            if form.is_valid():
                invoice = form.save()
        else:
            form = form_class(initial={'admin_notes':invoice.admin_notes})
    else:
        form = None
    
    invoice_display = invoice_html_display(request, invoice)
    notify = request.GET.get('notify', '')
    if guid==None: guid=''
    
    return render_to_response(template_name, {'invoice': invoice,
                                              'guid':guid, 
                                              'notify': notify, 
                                              'form':form,
                                              'invoice_display':invoice_display}, 
        context_instance=RequestContext(request))
    
def search(request, template_name="invoices/search.html"):
    invoices = Invoice.objects.all().order_by('-create_dt')
    return render_to_response(template_name, {'invoices': invoices}, 
        context_instance=RequestContext(request))
    
def adjust(request, id, form_class=AdminAdjustForm, template_name="invoices/adjust.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)
    #original_total = invoice.total
    #original_balance = invoice.balance

    if not is_admin(request.user): return Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            invoice.total += invoice.variance 
            invoice.balance += invoice.total - invoice.payments_credits 
            invoice.save()
            
            # make accounting entries
            from accountings.models import AcctEntry
            ae = AcctEntry.objects.create_acct_entry(request.user, 'invoice', invoice.id)
            if invoice.variance < 0:
                #this is a discount
                #makeacctentries_discount
                pass
                
            else:
                from accountings.utils import make_acct_entries_initial
                make_acct_entries_initial(request.user, ae, invoice.variance)
            
            return HttpResponseRedirect(invoice.get_absolute_url())
            
    else:
        form = form_class(initial={'variance':0.00, 'variance_notes':invoice.variance_notes})
        
    return render_to_response(template_name, {'invoice': invoice,
                                              'form':form}, 
        context_instance=RequestContext(request))
    
    
    
    
