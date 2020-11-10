

from builtins import str
from datetime import datetime, time, timedelta
import time as ttime
import subprocess

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.template.loader import get_template

from tendenci.libs.utils import python_executable
from tendenci.apps.base.decorators import password_required
from tendenci.apps.base.http import Http403
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.perms.decorators import is_enabled, superuser_required
from tendenci.apps.perms.utils import has_perm, update_perms_and_save
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.notifications.utils import send_notifications
from tendenci.apps.payments.forms import MarkAsPaidForm
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.invoices.forms import AdminNotesForm, AdminVoidForm, AdminAdjustForm, InvoiceSearchForm, EmailInvoiceForm
from tendenci.apps.invoices.utils import invoice_pdf
from tendenci.apps.emails.models import Email
from tendenci.apps.site_settings.utils import get_setting


@is_enabled('invoices')
def view(request, id, guid=None, form_class=AdminNotesForm, template_name="invoices/view.html"):
    """
    Invoice information, payment attempts (successful and unsuccessful).
    """
    if get_setting("module", "invoices", "disallow_private_urls"):
        guid = None
        if not request.user.is_authenticated:
            raise Http403

    invoice = get_object_or_404(Invoice.objects.all_invoices(), pk=id)

    if not invoice.allow_view_by(request.user, guid):
        raise Http403

    allowed_tuple = (
        request.user.profile.is_superuser,
        has_perm(request.user, 'invoices.change_invoice'))

    form = None
    if any(allowed_tuple):
        if request.method == "POST":
            form = form_class(request.POST, instance=invoice)
            if form.is_valid():
                invoice = form.save()
                EventLog.objects.log(instance=invoice)
        else:
            form = form_class(initial={'admin_notes': invoice.admin_notes})

    notify = request.GET.get('notify', u'')
    guid = guid or u''

    # boolean value
    merchant_login = get_setting("site", "global", "merchantaccount") != 'asdf asdf asdf'

    obj = invoice.get_object()
    obj_name = u''

    if obj:
        obj_name = obj._meta.verbose_name

    return render_to_resp(request=request, template_name=template_name,
        context={
        'invoice': invoice,
        'obj': obj,
        'obj_name': obj_name,
        'guid': guid,
        'notify': notify,
        'form': form,
        'can_pay': invoice.allow_payment_by(request.user, guid),
        'merchant_login': merchant_login})


def mark_as_paid(request, id, template_name='invoices/mark-as-paid.html'):
    """
    Makes a payment-record with a specified date/time
    payment method and payment amount.
    """
    invoice = get_object_or_404(Invoice, pk=id)

    if not has_perm(request.user, 'payments.change_payment'):
        raise Http403

    if request.method == 'POST':
        form = MarkAsPaidForm(request.POST)

        if form.is_valid():

            # make payment record
            payment = form.save(
                user=request.user,
                invoice=invoice,
                commit=False)

            payment = update_perms_and_save(request, form, payment)

            # update invoice; make accounting entries
            action_taken = invoice.make_payment(payment.creator,
                                                payment.amount)
            if action_taken:
                EventLog.objects.log(instance=invoice)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _('Payment successfully made'))

            return redirect(invoice)

    else:
        form = MarkAsPaidForm(initial={
            'amount': invoice.balance, 'submit_dt': datetime.now()})

    return render_to_resp(
        request=request, template_name=template_name, context={
            'invoice': invoice,
            'form': form,
        })


def mark_as_paid_old(request, id):
    """
    Sets invoice balance to 0 and adds
    accounting entries
    """
    invoice = get_object_or_404(Invoice, pk=id)

    if not request.user.profile.is_superuser:
        raise Http403

    action_taken = invoice.make_payment(request.user, invoice.balance)

    if action_taken:
        EventLog.objects.log(instance=invoice)

        messages.add_message(
            request,
            messages.SUCCESS,
            _('Successfully marked invoice %(pk)s as paid.' % {'pk':invoice.pk}))

    return redirect(invoice)


def void_payment(request, id):

    invoice = get_object_or_404(Invoice, pk=id)

    if not (request.user.profile.is_superuser): raise Http403

    amount = invoice.payments_credits
    invoice.void_payment(request.user, amount)

    EventLog.objects.log(instance=invoice)

    messages.add_message(request, messages.SUCCESS, _('Successfully voided payment for Invoice %(pk)s.' % {'pk':invoice.id}))
    return redirect(invoice)

@superuser_required
def void_invoice(request, id, form_class=AdminVoidForm, template_name="invoices/void.html"):
    """
    Voids invoice
    """
    invoice = get_object_or_404(Invoice, pk=id)
    form = form_class(request.POST or None, instance=invoice)
    obj = invoice.get_object()
    has_memberships = obj and hasattr(obj, 'memberships')
    has_registration= obj and hasattr(obj, 'event')

    if has_memberships:
        del form.fields['cancle_registration']
    elif has_registration:
        del form.fields['delete_membership']
    else:
        del form.fields['cancle_registration']
        del form.fields['delete_membership']
    
    if request.method == "POST":
        if form.is_valid():
            invoice = form.save()

            if invoice.payments_credits:
                invoice.void_payment(request.user, invoice.payments_credits)

            invoice.void(user=request.user)
            
            # cancel corresponding event registration
            if has_registration and form.cleaned_data.get('cancle_registration', False):
                if obj.__class__.__name__ == 'Registration':
                    registrants = obj.registrant_set.filter(cancel_dt__isnull=True)
                    for registrant in registrants:
                        registrant.cancel_dt = datetime.now()
                        registrant.save()
                    obj.canceled = True
                    obj.save()
            
            # delete corresponding memberships
            if has_memberships and form.cleaned_data.get('delete_membership', False):
                if obj.__class__.__name__ == 'MembershipSet':
                    for membership in obj.memberships():
                        if membership.status_detail != 'archive':
                            membership.delete()
            
            EventLog.objects.log(instance=invoice)
            
            return redirect(invoice.get_absolute_url())
    
    return render_to_resp(request=request, template_name=template_name,
        context={'invoice': invoice, 'form':form})

def unvoid_invoice(self, id):
    """
    Sets Invoice.is_void=False
    """
    invoice = get_object_or_404(Invoice.objects.void(), pk=id)
    invoice.unvoid()
    return redirect(invoice)

@is_enabled('invoices')
@login_required
def search(request, template_name="invoices/search.html"):
    start_amount = None
    end_amount = None
    tendered = None
    balance = None
    last_name = None
    start_dt = None
    end_dt = None
    search_criteria = None
    search_text = None
    search_method = None
    invoice_type = u''
    event = None
    event_id = None

    form = InvoiceSearchForm(request.GET)

    if form.is_valid():
        start_dt = form.cleaned_data.get('start_dt')
        end_dt = form.cleaned_data.get('end_dt')
        start_amount = form.cleaned_data.get('start_amount')
        end_amount = form.cleaned_data.get('end_amount')
        tendered = form.cleaned_data.get('tendered')
        balance = form.cleaned_data.get('balance')
        last_name = form.cleaned_data.get('last_name')
        search_criteria = form.cleaned_data.get('search_criteria')
        search_text = form.cleaned_data.get('search_text')
        search_method = form.cleaned_data.get('search_method')
        invoice_type = form.cleaned_data.get('invoice_type')
        event = form.cleaned_data.get('event')
        event_id = form.cleaned_data.get('event_id')

    if tendered:
        if 'void' in tendered:
            invoices = Invoice.objects.void()
        else:
            invoices = Invoice.objects.filter(status_detail=tendered)
    else:
        invoices = Invoice.objects.all()

    if start_dt:
        invoices = invoices.filter(create_dt__gte=datetime.combine(start_dt, time.min))
    if end_dt:
        invoices = invoices.filter(create_dt__lte=datetime.combine(end_dt, time.max))

    if start_amount:
        invoices = invoices.filter(total__gte=start_amount)
    if end_amount:
        invoices = invoices.filter(total__lte=end_amount)

    if balance == '0':
        invoices = invoices.filter(balance=0)
    elif balance == '1':
        invoices = invoices.filter(balance__gt=0)

    if last_name:
        invoices = invoices.filter(bill_to_last_name__iexact=last_name)

    owner = None
    if search_criteria and search_text:
        if search_criteria == 'owner_id':
            search_criteria = 'owner__id'
            try:
                search_text = int(search_text)
                [owner] = User.objects.filter(id=search_text)[:1] or [None]
            except:
                search_text = 0

        if search_method == 'starts_with':
            if isinstance(search_text, str):
                search_type = '__istartswith'
            else:
                search_type = '__startswith'
        elif search_method == 'contains':
            if isinstance(search_text, str):
                search_type = '__icontains'
            else:
                search_type = '__contains'
        else:
            if isinstance(search_text, str):
                search_type = '__iexact'
            else:
                search_type = '__exact'

        if all([search_criteria == 'owner__id',
                search_method == 'exact',
                owner]):
            invoices = invoices.filter(Q(bill_to_email__iexact=owner.email)
                               | Q(owner_id=owner.id))
        else:
            search_filter = {'%s%s' % (search_criteria,
                                       search_type): search_text}
            invoices = invoices.filter(**search_filter)

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

    if request.user.profile.is_superuser or has_perm(request.user, 'invoices.view_invoice'):
        invoices = invoices.order_by('-create_dt')
    else:
        invoices = invoices.filter(Q(creator=request.user) |
                                   Q(owner=request.user) |
                                   Q(bill_to_email__iexact=request.user.email)
                                   ).order_by('-create_dt')
    EventLog.objects.log()
    return render_to_resp(request=request, template_name=template_name,
        context={'invoices': invoices, 'form':form,})


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
            print(i.title, i.object_id, i.object_type)

            ct = ContentType.objects.get_for_model(Invoice)
            print(ct, ct.__module__, ct.pk, i.pk)

#            invoice_ids = invoices_objects.value_list('object_id', flat=True).filter(content_type = ct)
#            events = Invoice.objects.filter(pk__in=event_ids)

#            if i.object_type == 'registration':
#                print('hello')
#            else: print('not')
        print(dir(ct))

    else:
        if request.user.is_authenticated:
            invoices = invoices.filter(Q(creator=request.user) | Q(owner=request.user)).order_by('-create_dt')
        else:
            raise Http403
    EventLog.objects.log()
    return render_to_resp(request=request, template_name=template_name,
        context={'invoices': invoices, 'query': query})


@is_enabled('invoices')
def adjust(request, id, form_class=AdminAdjustForm, template_name="invoices/adjust.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)
    original_total = invoice.total
    original_balance = invoice.balance
    original_variance = invoice.variance

    if not (request.user.profile.is_superuser or has_perm(request.user, 'invoices.change_invoice')): raise Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            
            variance_changed = invoice.variance - original_variance
            invoice.total += variance_changed
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
            if variance_changed < 0:
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

            elif variance_changed > 0:
                from tendenci.apps.accountings.utils import make_acct_entries_initial
                make_acct_entries_initial(request.user, ae, variance_changed)

            return HttpResponseRedirect(invoice.get_absolute_url())

    else:
        form = form_class(initial={'variance': invoice.variance, 'variance_notes':invoice.variance_notes})

    return render_to_resp(request=request, template_name=template_name,
        context={'invoice': invoice,
                                              'form':form})


@is_enabled('invoices')
def detail(request, id, template_name="invoices/detail.html"):
    invoice = get_object_or_404(Invoice.objects.all_invoices(), pk=id)

    allowed_list = (
        request.user.profile.is_superuser,
        has_perm(request.user, 'invoices.change_invoice')
    )

    if not any(allowed_list):
        raise Http403

    from tendenci.apps.accountings.models import AcctEntry
    acct_entries = AcctEntry.objects.filter(object_id=id)

    # to be calculated in accounts_tags
    total_debit, total_credit = 0, 0

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
        account_numbers.append({
            "account_number": row[0],
            "description": row[1],
            "total": abs(row[2])})

    EventLog.objects.log(instance=invoice)

    print('here')

    return render_to_resp(request=request, template_name=template_name,
        context={
        'invoice': invoice,
        'account_numbers': account_numbers,
        'acct_entries': acct_entries,
        'total_debit': total_debit,
        'total_credit': total_credit})


@is_enabled('invoices')
def download_pdf(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    if not has_perm(request.user, 'invoices.change_invoice', invoice):
        raise Http403

    result = invoice_pdf(request, invoice)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice_{}.pdf"'.format(invoice.id)
    return response


@staff_member_required
def email_invoice(request, invoice_id, form_class=EmailInvoiceForm,
                  template_name='invoices/email_invoice.html'):
    if not request.user.profile.is_superuser:
        raise Http403

    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if request.method == "POST":
        email = Email()
        form = form_class(request.POST, instance=email)

        if form.is_valid():
            email = form.save(commit=False)
            email.sender_display = request.user.get_full_name()
            email.reply_to = request.user.email
            email.recipient = form.cleaned_data['recipient']
            email.content_type = "html"
            email.recipient_cc = form.cleaned_data['cc']

            attachment = form.cleaned_data['attachment']
            kwargs = {}
            if attachment:
                result = invoice_pdf(request, invoice)
                kwargs['attachments'] = [("invoice_{}.pdf".format(invoice.id),
                                      result.getvalue())]
            email.send(**kwargs)

            EventLog.objects.log(instance=email)
            msg_string = 'Successfully sent email invoice to {}.'.format(email.recipient)
            messages.add_message(request, messages.SUCCESS, msg_string)

            return HttpResponseRedirect(reverse('invoice.view', args=([invoice_id])))

    else:
        template = get_template("invoices/email_invoice_template.html")
        body_initial = template.render(context={'invoice': invoice}, request=request)
        form = form_class(initial={'subject': 'Invoice for {}'.format(invoice.title),
                                   'recipient': invoice.bill_to_email,
                                   'body': body_initial})

    return render_to_resp(request=request, template_name=template_name,context={
        'invoice': invoice,
        'form': form
        })

@staff_member_required
def report_top_spenders(request, template_name="reports/top_spenders.html"):
    """Show dollars per user report"""
    if not request.user.is_superuser:
        raise Http403

    entry_list = User.objects.order_by('-profile__total_spend')[:10]

    return render_to_resp(request=request, template_name=template_name, context={
        'entry_list': entry_list,
    })


@is_enabled('invoices')
@login_required
@password_required
def export(request, template_name="invoices/export.html"):
    """Export Invoices"""
    if not request.user.profile.is_superuser:
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

        identifier = int(ttime.time())
        temp_file_path = 'export/invoices/%s_temp.csv' % identifier
        default_storage.save(temp_file_path, ContentFile(''))

        # start the process
        subprocess.Popen([python_executable(), "manage.py",
                          "invoice_export_process",
                          '--start_dt=%s' % start_dt,
                          '--end_dt=%s' % end_dt,
                          '--identifier=%s' % identifier,
                          '--user=%s' % request.user.id])

        # log an event
        EventLog.objects.log()
        return redirect('invoice.export_status', identifier)
    else:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=30)

    context = {'start_dt': start_dt, 'end_dt': end_dt}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('invoices')
@login_required
@password_required
def export_status(request, identifier, template_name="invoices/export_status.html"):
    """Display export status"""
    if not request.user.profile.is_superuser:
        raise Http403

    export_path = 'export/invoices/%s.csv' % identifier
    download_ready = False
    if default_storage.exists(export_path):
        download_ready = True
    else:
        temp_export_path = 'export/invoices/%s_temp.csv' % identifier
        if not default_storage.exists(temp_export_path) and \
                not default_storage.exists(export_path):
            raise Http404

    context = {'identifier': identifier,
               'download_ready': download_ready}
    return render_to_resp(request=request, template_name=template_name, context=context)


@is_enabled('invoices')
@login_required
@password_required
def export_download(request, identifier):
    """Download the directories export."""
    if not request.user.profile.is_superuser:
        raise Http403

    file_name = '%s.csv' % identifier
    file_path = 'export/invoices/%s' % file_name
    if not default_storage.exists(file_path):
        raise Http404

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="invoice_export_%s"' % file_name
    response.content = default_storage.open(file_path).read()
    return response
