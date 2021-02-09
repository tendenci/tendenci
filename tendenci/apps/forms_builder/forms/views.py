# Special encoding for sending the email messsages with
# non-ascii characters.
# from __future__ import must occur at the beginning of the file
import datetime
import random
import string
import time
import csv

from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
# from djcelery.models import TaskMeta

from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import template_exists
from tendenci.apps.perms.utils import (has_perm, update_perms_and_save,
    get_query_filters, has_view_perm)
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.profiles.models import Profile
from tendenci.apps.recurring_payments.models import RecurringPayment
from tendenci.apps.recurring_payments.forms import RecurringPaymentForm
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.forms_builder.forms.forms import (
    FormForForm, FormForm, FormForField, PricingForm, BillingForm
)
from tendenci.apps.forms_builder.forms.models import Form, Field, FormEntry, Pricing
from tendenci.apps.forms_builder.forms.utils import (generate_admin_email_body,
    generate_submitter_email_body, generate_email_subject,
    make_invoice_for_entry, update_invoice_for_entry)
from tendenci.apps.forms_builder.forms.formsets import BaseFieldFormSet
from tendenci.apps.forms_builder.forms.tasks import FormEntriesExportTask
from tendenci.apps.emails.models import Email


@is_enabled('forms')
@login_required
def add(request, form_class=FormForm, template_name="forms/add.html"):
    if not has_perm(request.user,'forms.add_form'):
        raise Http403

    PricingFormSet = inlineformset_factory(Form, Pricing, form=PricingForm, extra=2, can_delete=False)

    formset = PricingFormSet()
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            form_instance = form.save(commit=False)
            # save form and associated pricings
            form_instance = update_perms_and_save(request, form, form_instance)
            formset = PricingFormSet(request.POST, instance=form_instance)
            if formset.is_valid():
                # update_perms_and_save does not appear to consider ManyToManyFields
                for method in form.cleaned_data['payment_methods']:
                    form_instance.payment_methods.add(method)

                formset.save()

                messages.add_message(request, messages.SUCCESS, _('Successfully added %(f)s' % {'f':form_instance}))
                return HttpResponseRedirect(reverse('form_field_update', args=[form_instance.pk]))
    else:
        form = form_class(user=request.user)

    return render_to_resp(request=request, template_name=template_name, context={
        'form':form,
        'formset': formset,
    })


@is_enabled('forms')
def edit(request, id, form_class=FormForm, template_name="forms/edit.html"):
    form_instance = get_object_or_404(Form, pk=id)

    if not has_perm(request.user,'forms.change_form',form_instance):
        raise Http403

    PricingFormSet = inlineformset_factory(Form, Pricing, form=PricingForm, extra=2)
#     RecurringPaymentFormSet = inlineformset_factory(Form, RecurringPayment, form=RecurringPaymentForm, extra=2)
    formset = PricingFormSet(request.POST or None, instance=form_instance)
    if request.method == "POST":
        form = form_class(request.POST, instance=form_instance, user=request.user)
        if form.is_valid() and formset.is_valid():
            form_instance = form.save(commit=False)
            form_instance = update_perms_and_save(request, form, form_instance)

            form.save_m2m()  # save payment methods
            formset.save()  # save price options

            # remove all pricings if no custom_payment form
            if not form.cleaned_data['custom_payment']:
                form_instance.pricing_set.all().delete()

            messages.add_message(request, messages.SUCCESS, _('Successfully edited %(f)s' % {'f': form_instance}))
            return HttpResponseRedirect(reverse('form_field_update', args=[form_instance.pk]))
    else:
        form = form_class(instance=form_instance, user=request.user)
    return render_to_resp(request=request, template_name=template_name,context={
        'form':form,
        'formset':formset,
        'form_instance':form_instance,
        })


@is_enabled('forms')
@login_required
def update_fields(request, id, template_name="forms/update_fields.html"):
    form_instance = get_object_or_404(Form, id=id)

    if not has_perm(request.user,'forms.add_form',form_instance):
        raise Http403

    form_class=inlineformset_factory(Form, Field, form=FormForField, formset=BaseFieldFormSet, extra=3)
    form_class._orderings = 'position'

    if request.method == "POST":
        form = form_class(request.POST, instance=form_instance, queryset=form_instance.fields.all().order_by('position'))
        if form.is_valid():
            form.save()
            EventLog.objects.log()
            messages.add_message(request, messages.SUCCESS, _('Successfully updated %(f)s' % {'f':form_instance}))
            return redirect('form_detail', form_instance.slug)
    else:
        form = form_class(instance=form_instance, queryset=form_instance.fields.all().order_by('position'))

    return render_to_resp(request=request, template_name=template_name,
        context={'form':form, 'form_instance':form_instance})


@is_enabled('forms')
@login_required
def delete(request, id, template_name="forms/delete.html"):
    form_instance = get_object_or_404(Form, pk=id)

    # check permission
    if not has_perm(request.user,'forms.delete_form',form_instance):
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(f)s' % {'f':form_instance}))

        form_instance.delete()
        return HttpResponseRedirect(reverse('forms'))

    return render_to_resp(request=request, template_name=template_name,
        context={'form': form_instance})


@is_enabled('forms')
@login_required
def copy(request, id):
    """
    Copies a form_instance and all the fields related to it.
    """
    form_instance = get_object_or_404(Form, pk=id)

    # check permission
    if not (has_perm(request.user,'forms.add_form',form_instance) and
        has_perm(request.user,'forms.change_form',form_instance)):
            raise Http403

    # create a new slug
    slug = form_instance.slug
    if len(slug.rsplit('-', 1)) > 1 and slug.rsplit('-', 1)[1].isdigit():
        slug = slug.rsplit('-', 1)[0]
    i = 1
    while True:
        if i > 0:
            if i > 1:
                slug = slug.rsplit("-", 1)[0]
            slug = "%s-%s" % (slug, i)
        match = Form.objects.filter(slug=slug)
        if not match:
            break
        i += 1

    # copy the form
    new_form = Form.objects.create(
        title = form_instance.title,
        slug = slug,
        intro = form_instance.intro,
        response = form_instance.response,
        email_text = form_instance.email_text,
        subject_template = form_instance.subject_template,
        send_email = form_instance.send_email,
        email_from = form_instance.email_from,
        email_copies = form_instance.email_copies,
        completion_url = form_instance.completion_url,
        template = form_instance.template,
        allow_anonymous_view = form_instance.allow_anonymous_view,
        allow_user_view = form_instance.allow_user_view,
        allow_member_view = form_instance.allow_member_view,
        allow_user_edit = form_instance.allow_user_edit,
        allow_member_edit = form_instance.allow_member_edit,
        creator = request.user,
        creator_username = request.user.username,
        owner = request.user,
        owner_username = request.user.username,
        status = True,
        status_detail = 'draft',
        )

    # copy form fields
    for field in form_instance.fields.all():
        Field.objects.create(
            form = new_form,
            label = field.label,
            field_type = field.field_type,
            field_function = field.field_function,
            required = field.required,
            visible = field.visible,
            choices = field.choices,
            position = field.position,
            default = field.default,
            )

    EventLog.objects.log(instance=form_instance)
    messages.add_message(request, messages.SUCCESS, _('Successfully added %(n)s' % {'n': new_form}))
    return redirect('admin:forms_form_change', new_form.pk)


@is_enabled('forms')
@login_required
def entries(request, id, template_name="forms/entries.html"):
    form = get_object_or_404(Form, pk=id)

    if not has_perm(request.user,'forms.change_form',form):
        raise Http403

    entries = form.entries.order_by('-entry_time')

    EventLog.objects.log(instance=form)

    return render_to_resp(request=request, template_name=template_name,
        context={'form':form,'entries': entries})


@is_enabled('forms')
@login_required
def entry_delete(request, id, template_name="forms/entry_delete.html"):
    entry = get_object_or_404(FormEntry, pk=id)

    # check permission
    if not has_perm(request.user,'forms.delete_form',entry.form):
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, _('Successfully deleted entry %(e)s' % { 'e': entry}))
        entry.delete()
        return HttpResponseRedirect(reverse('forms'))

    return render_to_resp(request=request, template_name=template_name,
        context={'entry': entry})


@is_enabled('forms')
@login_required
def entry_detail(request, id, template_name="forms/entry_detail.html"):
    entry = get_object_or_404(FormEntry, pk=id)

    # check permission
    if not has_perm(request.user,'forms.change_form',entry.form):
        raise Http403

    form_template = entry.form.template
    if not form_template or not template_exists(form_template):
        form_template = "forms/base.html"

    return render_to_resp(request=request, template_name=template_name,
        context={'entry':entry,
                                              'form': entry.form,
                                              'form_template': form_template})


@is_enabled('forms')
def entries_export(request, id, include_files=False):
    form_instance = get_object_or_404(Form, pk=id)

    # check permission
    if not has_perm(request.user,'forms.change_form',form_instance):
        raise Http403

    EventLog.objects.log(instance=form_instance)

    entries = form_instance.entries.all()

    if entries:
        if not settings.CELERY_IS_ACTIVE:
            task = FormEntriesExportTask()
            response = task.run(form_instance, entries, include_files)
            return response
        else:
            task = FormEntriesExportTask.delay(form_instance, entries, include_files)
            task_id = task.task_id
            return redirect('form_entries_export_status', task_id)
    else:
        # blank csv document
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_entries_%d.csv"' % time.time()
        delimiter = ','

        csv.writer(response, delimiter=delimiter)

    return response

def entries_export_status(request, task_id, template_name="forms/entry_export_status.html"):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None

    return render_to_resp(request=request, template_name=template_name, context={
        'task':task,
        'task_id':task_id,
        'user_this':None,
    })

def entries_export_check(request, task_id):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None

    if task and task.status == "SUCCESS":
        return HttpResponse("OK")
    else:
        return HttpResponse("DNE")

def entries_export_download(request, task_id):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None

    if task and task.status == "SUCCESS":
        return task.result
    else:
        raise Http404


@is_enabled('forms')
def search(request, template_name="forms/search.html"):
    if not has_perm(request.user,'forms.view_form'):
        raise Http403

    filters = get_query_filters(request.user, 'forms.view_form')
    forms = Form.objects.filter(filters).distinct()
    query = request.GET.get('q', None)
    if query:
        forms = forms.filter(Q(title__icontains=query) | Q(intro__icontains=query) | Q(response__icontains=query))

    forms = forms.order_by('-pk')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'forms':forms})


@is_enabled('forms')
def form_detail(request, slug, template="forms/form_detail.html"):
    """
    Display a built form and handle submission.
    """
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, slug=slug)

    if not has_view_perm(request.user,'forms.view_form',form):
        raise Http403

    # If form has a recurring payment, make sure the user is logged in
    if form.recurring_payment:
        [email_field] = form.fields.filter(field_type__iexact='EmailVerificationField')[:1] or [None]
        if request.user.is_anonymous and not email_field:
            # anonymous user - if we don't have the email field, redirect to login
            response = redirect('auth_login')
            response['Location'] += '?next=%s' % form.get_absolute_url()
            return response
        if request.user.is_superuser and not email_field:
            messages.add_message(request, messages.WARNING,
                    'Please edit the form to include an email field ' +
                    'as it is required for setting up a recurring ' +
                    'payment for anonymous users.')

    if form.custom_payment and not form.recurring_payment:
        billing_form = BillingForm(request.POST or None)
        if request.user.is_authenticated:
            billing_form.initial = {
                        'first_name':request.user.first_name,
                        'last_name':request.user.last_name,
                        'email':request.user.email}
    else:
        billing_form = None

    form_for_form = FormForForm(form, request.user, request.POST or None, request.FILES or None)
    
    for field in form_for_form.fields:
        field_default = request.GET.get(field, None)
        if field_default:
            form_for_form.fields[field].initial = field_default

    if request.method == "POST":
        if form_for_form.is_valid() and (not billing_form or billing_form.is_valid()):
            entry = form_for_form.save()
            entry.entry_path = request.POST.get("entry_path", "")
            if request.user.is_anonymous:
                entry.creator = entry.check_and_create_user()
            else:
                entry.creator = request.user
            entry.save()
            entry.set_group_subscribers()

            # Email
            subject = generate_email_subject(form, entry)
            email_headers = {}  # content type specified below
            if form.email_from:
                email_headers.update({'Reply-To':form.email_from})

            # Email to submitter
            # fields aren't included in submitter body to prevent spam
            submitter_body = generate_submitter_email_body(entry, form_for_form)
            email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
            email_to = form_for_form.email_to()
            is_spam = Email.is_blocked(email_to)
            if is_spam:
                # log the spam
                description = "Email \"{0}\" blocked because it is listed in email_blocks.".format(email_to)
                EventLog.objects.log(instance=form, description=description)

                if form.completion_url:
                    return HttpResponseRedirect(form.completion_url)
                return redirect("form_sent", form.slug)

            email = Email()
            email.subject = subject
            email.reply_to = form.email_from

            if email_to and form.send_email and form.email_text:
                # Send message to the person who submitted the form.
                email.recipient = email_to
                email.body = submitter_body
                email.send(fail_silently=getattr(settings, 'EMAIL_FAIL_SILENTLY', True))
                # log an event
                EventLog.objects.log(instance=form, description='Confirmation email sent to {}'.format(email_to))

            # Email copies to admin
            admin_body = generate_admin_email_body(entry, form_for_form, user=request.user)
            email_from = email_to or email_from # Send from the email entered.
            email_headers = {}  # Reset the email_headers
            email_headers.update({'Reply-To':email_from})
            email_copies = [e.strip() for e in form.email_copies.split(',') if e.strip()]

            subject = subject.encode(errors='ignore')
            email_recipients = entry.get_function_email_recipients()
            # reply_to of admin emails goes to submitter
            email.reply_to = email_to

            if email_copies or email_recipients:
                # prepare attachments
                attachments = []
                # Commenting out the attachment block to not add attachments to the email for the reason below:
                # According to SES message quotas https://docs.aws.amazon.com/ses/latest/DeveloperGuide/quotas.html, 
                # the maximum message size (including attachments) is 10 MB per message (after base64 encoding) 
                # which means the actual size should be less than 7.5 MB or so because text after encoded with the BASE64 
                # algorithm increases its size by 1/3. But the allowed upload size is much larger than 7.5 MB.
#                 try:
#                     for f in form_for_form.files.values():
#                         f.seek(0)
#                         attachments.append((f.name, f.read()))
#                 except ValueError:
#                     attachments = []
#                     for field_entry in entry.fields.all():
#                         if field_entry.field.field_type == 'FileField':
#                             try:
#                                 f = default_storage.open(field_entry.value)
#                             except IOError:
#                                 pass
#                             else:
#                                 f.seek(0)
#                                 attachments.append((f.name.split('/')[-1], f.read()))

                fail_silently = getattr(settings, 'EMAIL_FAIL_SILENTLY', True)
                # Send message to the email addresses listed in the copies
                if email_copies:
                    email.body = admin_body
                    email.recipient = email_copies
#                     if request.user.is_anonymous or not request.user.is_active:
#                         email.content_type = 'text'
                    email.send(fail_silently=fail_silently, attachments=attachments)

                # Email copies to recipient list indicated in the form
                if email_recipients:
                    email.body = admin_body
                    email.recipient = email_recipients
                    email.send(fail_silently=fail_silently, attachments=attachments)

            # payment redirect
            if (form.custom_payment or form.recurring_payment) and entry.pricing:
                # get the pricing's price, custom or otherwise
                price = entry.pricing.price or form_for_form.cleaned_data.get('custom_price')

                if form.recurring_payment:
                    if request.user.is_anonymous:
                        rp_user = entry.creator
                    else:
                        rp_user = request.user
                    billing_start_dt = datetime.datetime.now()
                    trial_period_start_dt = None
                    trial_period_end_dt = None
                    if entry.pricing.has_trial_period:
                        trial_period_start_dt = datetime.datetime.now()
                        trial_period_end_dt = trial_period_start_dt + datetime.timedelta(1)
                        billing_start_dt = trial_period_end_dt
                    # Create recurring payment
                    rp = RecurringPayment(
                             user=rp_user,
                             description=form.title,
                             billing_period=entry.pricing.billing_period,
                             billing_start_dt=billing_start_dt,
                             num_days=entry.pricing.num_days,
                             due_sore=entry.pricing.due_sore,
                             payment_amount=price,
                             taxable=entry.pricing.taxable,
                             tax_rate=entry.pricing.tax_rate,
                             has_trial_period=entry.pricing.has_trial_period,
                             trial_period_start_dt=trial_period_start_dt,
                             trial_period_end_dt=trial_period_end_dt,
                             trial_amount=entry.pricing.trial_amount,
                             creator=rp_user,
                             creator_username=rp_user.username,
                             owner=rp_user,
                             owner_username=rp_user.username,
                         )
                    rp.save()
                    if rp.platform == 'authorizenet':
                        rp.add_customer_profile()

                    # redirect to recurring payments
                    messages.add_message(request, messages.SUCCESS, _('Successful transaction.'))
                    return redirect('recurring_payment.view_account', rp.id, rp.guid)
                else:
                    # create the invoice
                    invoice = make_invoice_for_entry(entry, custom_price=price)

                    update_invoice_for_entry(invoice, billing_form)

                    # log an event for invoice add
                    EventLog.objects.log(instance=form)

                    # redirect to online payment
                    if invoice.balance > 0:
                        if (entry.payment_method.machine_name).lower() == 'credit-card':
                            return redirect('payment.pay_online', invoice.id, invoice.guid)
                        # redirect to invoice page
                        return redirect('invoice.view', invoice.id, invoice.guid)

            # default redirect
            if form.completion_url:
                completion_url = form.completion_url.strip().replace('[entry_id]', str(entry.id))
                return HttpResponseRedirect(completion_url)
            return redirect("form_sent", form.slug)

    # set form's template to forms/base.html if no template or template doesn't exist
    if not form.template or not template_exists(form.template):
        form.template = "forms/base.html"

    context = {
        "form": form,
        'billing_form': billing_form,
        "form_for_form": form_for_form,
        'form_template': form.template,
    }
    return render_to_resp(request=request, template_name=template, context=context)


def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, slug=slug)
    # set form's template to default if no template or template doesn't exist
    if not form.template or not template_exists(form.template):
        form.template = "default.html"
    context = {"form": form, "form_template": form.template}
    return render_to_resp(request=request, template_name=template, context=context)


@is_enabled('forms')
def form_entry_payment(request, invoice_id, invoice_guid, form_class=BillingForm, template="forms/form_payment.html"):
    """
    Show billing form, update the invoice then proceed to external payment.
    """
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if not invoice.allow_view_by(request.user, invoice_guid):
        raise Http403

    entry = FormEntry.objects.get(id=invoice.object_id)

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            update_invoice_for_entry(invoice, form)
            # redirect to online payment
            if (entry.payment_method.machine_name).lower() == 'credit-card':
                return redirect('payment.pay_online', invoice.id, invoice.guid)
            # redirect to invoice page
            return redirect('invoice.view', invoice.id, invoice.guid)
    else:
        if request.user.is_authenticated:
            form = form_class(initial={
                        'first_name':request.user.first_name,
                        'last_name':request.user.last_name,
                        'email':request.user.email})
        else:
            form = form_class()
    # set form's template to default if no template or template doesn't exist
    form_template = entry.form.template
    if not form_template or not template_exists(form_template):
        form_template = "default.html"
    EventLog.objects.log(instance=entry)
    return render_to_resp(request=request, template_name=template, context={
            'payment_form':form,
            'form':entry.form,
            'form_template': form_template,
        })


@is_enabled('forms')
@login_required
def export(request, template_name="forms/export.html"):
    """Export forms"""
    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        export_id = run_export_task('forms_builder.forms', 'form', [])
        EventLog.objects.log()
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })


@is_enabled('forms')
@login_required
def files(request, id):
    """
    Returns file.  Allows us to handle privacy.

    If default storage is remote:
        We can get data from remote location, convert to file
        object and return a file response.
    """
    import os
    import mimetypes
    from django.core.files.base import ContentFile
    from tendenci.apps.forms_builder.forms.models import FieldEntry

    field = get_object_or_404(FieldEntry, pk=id)
    form = field.field.form

    base_name = os.path.basename(field.value)
    mime_type = mimetypes.guess_type(base_name)[0]

    if not has_perm(request.user,'forms.change_form', form):
        raise Http403

    if not mime_type:
        raise Http404

    if not default_storage.exists(field.value):
        raise Http404

    data = default_storage.open(field.value).read()
    f = ContentFile(data)

    EventLog.objects.log()
    response = HttpResponse(f.read(), content_type=mime_type)
    response['Content-Disposition'] = 'filename="%s"' % base_name
    return response
