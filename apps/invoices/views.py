from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import settings

from base.http import Http403
from theme.shortcuts import themed_response as render_to_response
from perms.utils import is_admin
from event_logs.models import EventLog
from notification.utils import send_notifications
from site_settings.utils import get_setting
from exports.tasks import TendenciExportTask

from invoices.models import Invoice
from invoices.forms import AdminNotesForm, AdminAdjustForm

def view(request, id, guid=None, form_class=AdminNotesForm, template_name="invoices/view.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)

    if not invoice.allow_view_by(request.user, guid): raise Http403
    
    if is_admin(request.user):
        if request.method == "POST":
            form = form_class(request.POST, instance=invoice)
            if form.is_valid():
                invoice = form.save()
                # log an event here for invoice edit
                log_defaults = {
                    'event_id' : 312000,
                    'event_data': '%s (%d) edited by %s' % (invoice._meta.object_name, invoice.pk, request.user),
                    'description': '%s edited' % invoice._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': invoice,
                }
                EventLog.objects.log(**log_defaults)  
        else:
            form = form_class(initial={'admin_notes':invoice.admin_notes})
    else:
        form = None
    
    notify = request.GET.get('notify', '')
    if guid==None: guid=''
    
    merchant_login = False
    if hasattr(settings, 'MERCHANT_LOGIN') and settings.MERCHANT_LOGIN:
        merchant_login = True
      
    obj = invoice.get_object()
    
    obj_name = ""
    if obj:
        obj_name = obj._meta.verbose_name
    
    return render_to_response(template_name, {'invoice': invoice,
                                              'obj': obj,
                                              'obj_name': obj_name,
                                              'guid':guid, 
                                              'notify': notify, 
                                              'form':form,
                                              'merchant_login': merchant_login}, 
        context_instance=RequestContext(request))
    
    
def search(request, template_name="invoices/search.html"):
    query = request.GET.get('q', None)
    bill_to_email = request.GET.get('bill_to_email', None)

    if get_setting('site', 'global', 'searchindex') and query:
        invoices = Invoice.objects.search(query)
    else:
        invoices = Invoice.objects.all()
        if bill_to_email:
            invoices = invoices.filter(bill_to_email=bill_to_email)
    if is_admin(request.user):
        invoices = invoices.order_by('-create_dt')
    else:
        if request.user.is_authenticated():
            from django.db.models import Q
            invoices = invoices.filter(Q(creator=request.user) | Q(owner=request.user)).order_by('-create_dt')
        else:
            raise Http403

    return render_to_response(template_name, {'invoices': invoices, 'query': query}, 
        context_instance=RequestContext(request))
    
def adjust(request, id, form_class=AdminAdjustForm, template_name="invoices/adjust.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)
    original_total = invoice.total
    original_balance = invoice.balance

    if not is_admin(request.user): raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            invoice.total += invoice.variance 
            invoice.balance = invoice.total - invoice.payments_credits 
            invoice.save()
            
            # log an event for invoice edit
            log_defaults = {
                'event_id' : 312000,
                'event_data': '%s (%d) edited by %s' % (invoice._meta.object_name, invoice.pk, request.user),
                'description': '%s edited' % invoice._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': invoice,
            }
            EventLog.objects.log(**log_defaults)
            
            notif_context = {
                'request': request,
                'object': invoice,
            }
            send_notifications('module','invoices','invoicerecipients',
                'invoice_edited', notif_context)
            
            # make accounting entries
            from accountings.models import AcctEntry
            ae = AcctEntry.objects.create_acct_entry(request.user, 'invoice', invoice.id)
            if invoice.variance < 0:
                from accountings.utils import make_acct_entries_discount
                #this is a discount
                opt_d = {}
                opt_d['discount'] = True
                opt_d['original_invoice_total'] = original_total
                opt_d['original_invoice_balance'] = original_balance
                opt_d['discount_account_number'] = 460100
                
                obj = invoice.get_object()
                if obj and hasattr(obj, 'get_acct_number'):
                    opt_d['discount_account_number'] = obj.get_acct_number(discount=True)
                
                make_acct_entries_discount(request.user, invoice, ae, opt_d)
                
            else:
                from accountings.utils import make_acct_entries_initial
                make_acct_entries_initial(request.user, ae, invoice.variance)
            
            return HttpResponseRedirect(invoice.get_absolute_url())
            
    else:
        form = form_class(initial={'variance':0.00, 'variance_notes':invoice.variance_notes})
        
    return render_to_response(template_name, {'invoice': invoice,
                                              'form':form}, 
        context_instance=RequestContext(request))
    
def detail(request, id, template_name="invoices/detail.html"):
    invoice = get_object_or_404(Invoice, pk=id)
    
    if not is_admin(request.user): raise Http403
    
    from accountings.models import AcctEntry
    acct_entries = AcctEntry.objects.filter(object_id=id)
    # to be calculated in accounts_tags
    total_debit = 0
    total_credit = 0
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
                SELECT DISTINCT account_number, description, sum(amount) as total 
                FROM accountings_acct 
                INNER JOIN accountings_accttran on accountings_accttran.account_id =accountings_acct.id 
                INNER JOIN accountings_acctentry on accountings_acctentry.id =accountings_accttran.acct_entry_id 
                WHERE accountings_acctentry.object_id = %d 
                GROUP BY account_number 
                ORDER BY account_number  """ % (invoice.id)) 
    account_numbers = []
    for row in cursor.fetchall():
        account_numbers.append({"account_number":row[0],
                                "description":row[1],
                                "total":abs(row[2])})
    
    return render_to_response(template_name, {'invoice': invoice,
                                              'account_numbers': account_numbers,
                                              'acct_entries':acct_entries,
                                              'total_debit':total_debit,
                                              'total_credit':total_credit}, 
                                              context_instance=RequestContext(request))
    
@login_required
def export(request, template_name="invoices/export.html"):
    """Export Invoices"""
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        # initilize initial values
        file_name = "invoices.xls"
        fields = [
            'guid',
            'object_type',
            'title',
            'tender_date',
            'bill_to',
            'bill_to_first_name',
            'bill_to_last_name',
            'bill_to_company',
            'bill_to_address',
            'bill_to_city',
            'bill_to_state',
            'bill_to_zip_code',
            'bill_to_country',
            'bill_to_phone',
            'bill_to_fax',
            'bill_to_email',
            'ship_to',
            'ship_to_first_name',
            'ship_to_last_name',
            'ship_to_company',
            'ship_to_address',
            'ship_to_city',
            'ship_to_state',
            'ship_to_zip_code',
            'ship_to_country',
            'ship_to_phone',
            'ship_to_fax',
            'ship_to_email',
            'ship_to_address_type',
            'receipt',
            'gift',
            'arrival_date_time',
            'greeting',
            'instructions',
            'po',
            'terms',
            'due_date',
            'ship_date',
            'ship_via',
            'fob',
            'project',
            'other',
            'message',
            'subtotal',
            'shipping',
            'shipping_surcharge',
            'box_and_packing',
            'tax_exempt',
            'tax_exemptid',
            'tax_rate',
            'taxable',
            'tax',
            'variance',
            'total',
            'payments_credits',
            'balance',
            'estimate',
            'disclaimer',
            'variance_notes',
            'admin_notes',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status_detail',
            'status',
        ]
        
        if not settings.CELERY_IS_ACTIVE:
            # if celery server is not present 
            # evaluate the result and render the results page
            result = TendenciExportTask()
            response = result.run(Invoice, fields, file_name)
            return response
        else:
            result = TendenciExportTask.delay(Invoice, fields, file_name)
            return redirect('export.status', result.task_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
