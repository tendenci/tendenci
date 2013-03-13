from __future__ import unicode_literals
from datetime import datetime, time, timedelta

from django.template import RequestContext
from django.db.models import Sum, Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.conf import settings

from tendenci.core.base.http import Http403
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.perms.decorators import is_enabled
from tendenci.core.perms.utils import has_perm
from tendenci.core.event_logs.models import EventLog
from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.notifications.utils import send_notifications

from tendenci.apps.invoices.utils import run_invoice_export_task
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.invoices.forms import AdminNotesForm, AdminAdjustForm, InvoiceSearchForm


@is_enabled('invoices')
def view(request, id, guid=None, form_class=AdminNotesForm, template_name="invoices/view.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)

    if not invoice.allow_view_by(request.user, guid): raise Http403
    
    if request.user.profile.is_superuser or has_perm(request.user, 'invoices.change_invoice'):
        if request.method == "POST":
            form = form_class(request.POST, instance=invoice)
            if form.is_valid():
                invoice = form.save()
                # log an event here for invoice edit
                EventLog.objects.log(instance=invoice)  
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


def mark_as_paid(request, id):
    
    invoice = get_object_or_404(Invoice, pk=id)
    
    if not (request.user.profile.is_superuser): raise Http403    
    
    balance = invoice.balance
    invoice.make_payment(request.user, balance)
    
    messages.add_message(request, messages.SUCCESS, 'Successfully marked invoice %s as paid.' % invoice.id)
    return redirect(invoice)


def void_payment(request, id):
    
    invoice = get_object_or_404(Invoice, pk=id)
    
    if not (request.user.profile.is_superuser): raise Http403    
    
    amount = invoice.payments_credits
    invoice.void_payment(request.user, amount)
    
    messages.add_message(request, messages.SUCCESS, 'Successfully voided payment for Invoice %s.' % invoice.id)
    return redirect(invoice)


@login_required
def search(request, template_name="invoices/search.html"):
    query = u''
    invoice_type = u''
    start_dt = None
    end_dt = None
    event = None
    event_id = None
    
    has_index = get_setting('site', 'global', 'searchindex')
    form = InvoiceSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('q')
        invoice_type = form.cleaned_data.get('invoice_type')
        start_dt = form.cleaned_data.get('start_dt')
        end_dt = form.cleaned_data.get('end_dt')
        event = form.cleaned_data.get('event')
        event_id = form.cleaned_data.get('event_id')
    
    bill_to_email = request.GET.get('bill_to_email', None)

    if has_index and query:
        invoices = Invoice.objects.search(query)
    else:
        invoices = Invoice.objects.all()
        if bill_to_email:
            invoices = invoices.filter(bill_to_email=bill_to_email)
    
    if invoice_type:
        content_type = ContentType.objects.filter(app_label=invoice_type)
        invoices = invoices.filter(object_type__in=content_type)
        if invoice_type == 'events':
            # Set event filters
            event_set = set()
            if event:
                event_set.add(event.pk)
            if event_id:
                event_set.add(event_id)
            if event or event_id:
                invoices = invoices.filter(registration__event__pk__in=event_set)
            
    if start_dt:
        invoices = invoices.filter(create_dt__gte=datetime.combine(start_dt, time.min))
     
    if end_dt:
        invoices = invoices.filter(create_dt__lte=datetime.combine(end_dt, time.max))
    
    if request.user.profile.is_superuser or has_perm(request.user, 'invoices.view_invoice'):
        invoices = invoices.order_by('-create_dt')
    else:
        if request.user.is_authenticated():
            from django.db.models import Q
            invoices = invoices.filter(Q(creator=request.user) | Q(owner=request.user)).order_by('-create_dt')
        else:
            raise Http403
    EventLog.objects.log()
    return render_to_response(template_name, {'invoices': invoices, 'query': query, 'form':form,}, 
        context_instance=RequestContext(request))


@login_required
def search_report(request, template_name="invoices/search.html"):
    from django.db.models import Q

    def is_number(num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    #query
    query = request.GET.get('q', None)
    invoices = Invoice.objects.all()
    if query:
        if is_number(query):
            invoices = invoices.filter( Q(pk=query) | Q(total=query)
                                      | Q(balance=query)  | Q(title__icontains=query) )
        else:
            invoices = invoices.filter( Q(title__icontains=query) )
    #permissions
    if request.user.profile.is_superuser or has_perm(request.user, 'invoices.view_invoice'):
        invoices = invoices.order_by('object_type', '-create_dt')

        for i in invoices: #[0:2]:
            print i.title, i.object_id, i.object_type

            ct = ContentType.objects.get_for_model(Invoice)
            print ct, ct.__module__, ct.pk, i.pk

#            invoice_ids = invoices_objects.value_list('object_id', flat=True).filter(content_type = ct)
#            events = Invoice.objects.filter(pk__in=event_ids)

#            if i.object_type == 'registration':
#                print 'hello'
#            else: print 'not'
        print dir(ct)

    else:
        if request.user.is_authenticated():
            invoices = invoices.filter(Q(creator=request.user) | Q(owner=request.user)).order_by('-create_dt')
        else:
            raise Http403
    EventLog.objects.log()
    return render_to_response(template_name, {'invoices': invoices, 'query': query},
        context_instance=RequestContext(request))


@is_enabled('discounts')
def adjust(request, id, form_class=AdminAdjustForm, template_name="invoices/adjust.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)
    original_total = invoice.total
    original_balance = invoice.balance

    if not (request.user.profile.is_superuser or has_perm(request.user, 'invoices.change_invoice')): raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            invoice.total += invoice.variance 
            invoice.balance = invoice.total - invoice.payments_credits 
            invoice.save()
            
            EventLog.objects.log(instance=invoice)
            
            notif_context = {
                'request': request,
                'object': invoice,
            }
            send_notifications('module','invoices','invoicerecipients',
                'invoice_edited', notif_context)
            
            # make accounting entries
            from tendenci.apps.accountings.models import AcctEntry
            ae = AcctEntry.objects.create_acct_entry(request.user, 'invoice', invoice.id)
            if invoice.variance < 0:
                from tendenci.apps.accountings.utils import make_acct_entries_discount
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
                from tendenci.apps.accountings.utils import make_acct_entries_initial
                make_acct_entries_initial(request.user, ae, invoice.variance)
            
            return HttpResponseRedirect(invoice.get_absolute_url())
            
    else:
        form = form_class(initial={'variance':0.00, 'variance_notes':invoice.variance_notes})
        
    return render_to_response(template_name, {'invoice': invoice,
                                              'form':form}, 
        context_instance=RequestContext(request))


@is_enabled('discounts')
def detail(request, id, template_name="invoices/detail.html"):
    invoice = get_object_or_404(Invoice, pk=id)

    if not (request.user.profile.is_superuser or has_perm(request.user, 'invoices.change_invoice')): raise Http403

    from tendenci.apps.accountings.models import AcctEntry
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
                GROUP BY account_number, description 
                ORDER BY account_number  """ % (invoice.id)) 
    account_numbers = []
    for row in cursor.fetchall():
        account_numbers.append({"account_number":row[0],
                                "description":row[1],
                                "total":abs(row[2])})

    EventLog.objects.log(instance=invoice)

    return render_to_response(template_name, {'invoice': invoice,
                                              'account_numbers': account_numbers,
                                              'acct_entries':acct_entries,
                                              'total_debit':total_debit,
                                              'total_credit':total_credit}, 
                                              context_instance=RequestContext(request))


@login_required
def export(request, template_name="invoices/export.html"):
    """Export Invoices"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        end_dt = request.POST.get('end_dt', None)
        start_dt = request.POST.get('start_dt', None)

        # First, convert our strings into datetime objects
        # in case we need to do a timedelta
        try:
            end_dt = datetime.strptime(end_dt, '%Y-%m-%d')
        except:
            end_dt = datetime.now()

        try:
            start_dt = datetime.strptime(start_dt, '%Y-%m-%d')
        except:
            start_dt = end_dt - timedelta(days=30)

        # convert our datetime objects back to strings
        # so we can pass them on to the task
        end_dt = end_dt.strftime("%Y-%m-%d")
        start_dt = start_dt.strftime("%Y-%m-%d")

        export_id = run_invoice_export_task('invoices', 'invoice', start_dt, end_dt)
        EventLog.objects.log()
        return redirect('export.status', export_id)
    else:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=30)

    return render_to_response(template_name, {
        'start_dt': start_dt,
        'end_dt': end_dt,
    }, context_instance=RequestContext(request))


@staff_member_required
def report_top_spenders(request, template_name="reports/top_spenders.html"):
    """Show dollars per user report"""
    if not request.user.is_superuser:
        raise Http403
    
    entry_list = []
    users = User.objects.all()
    for user in users:
        invoices = Invoice.objects.filter(Q(creator=user) | Q(owner=user) | Q(bill_to_email=user.email)).aggregate(Sum('total'))
        if invoices['total__sum'] is not None and invoices['total__sum'] > 0:
            entry_list.append({'user':user, 'invoices':invoices})

    entry_list = sorted(entry_list, key=lambda entry:entry['invoices']['total__sum'], reverse=True)[:20]

    return render_to_response(template_name, {
        'entry_list': entry_list,
    }, context_instance=RequestContext(request))
