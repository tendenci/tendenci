# Special encoding for sending the email messsages with
# non-ascii characters.
# from __future__ import must occur at the beginning of the file
from __future__ import unicode_literals
import datetime, random, string

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.utils.encoding import smart_str
from django.template.defaultfilters import yesno
from django.core.files.storage import default_storage
from django.template.loader import get_template
from django.contrib.auth.models import User
from djcelery.models import TaskMeta

from tendenci.core.perms.decorators import is_enabled
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.base.http import Http403
from tendenci.core.base.utils import check_template, template_exists
from tendenci.core.perms.utils import (has_perm, update_perms_and_save,
    get_query_filters, has_view_perm)
from tendenci.core.event_logs.models import EventLog
from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.profiles.models import Profile
from tendenci.addons.recurring_payments.models import RecurringPayment
from tendenci.core.exports.utils import run_export_task

from tendenci.apps.forms_builder.forms.forms import (FormForForm, FormForm, FormForField,
    PricingForm, BillingForm)
from tendenci.apps.forms_builder.forms.models import Form, Field, FormEntry, Pricing
from tendenci.apps.forms_builder.forms.utils import (generate_admin_email_body,
    generate_submitter_email_body, generate_email_subject,
    make_invoice_for_entry, update_invoice_for_entry)
from tendenci.apps.forms_builder.forms.formsets import BaseFieldFormSet
from tendenci.apps.forms_builder.forms.tasks import FormEntriesExportTask


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

                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % form_instance)
                return HttpResponseRedirect(reverse('form_field_update', args=[form_instance.pk]))
    else:
        form = form_class(user=request.user)

    return render_to_response(template_name, {
        'form':form,
        'formset':formset,
    }, context_instance=RequestContext(request))


@is_enabled('forms')
def edit(request, id, form_class=FormForm, template_name="forms/edit.html"):
    form_instance = get_object_or_404(Form, pk=id)

    if not has_perm(request.user,'forms.change_form',form_instance):
        raise Http403

    PricingFormSet = inlineformset_factory(Form, Pricing, form=PricingForm, extra=2)

    if request.method == "POST":
        form = form_class(request.POST, instance=form_instance, user=request.user)
        if form_instance.recurring_payment:
            formset = RecurringPaymentFormSet(request.POST, instance=form_instance)
        else:
            formset = PricingFormSet(request.POST, instance=form_instance)
        if form.is_valid() and formset.is_valid():
            form_instance = form.save(commit=False)
            form_instance = update_perms_and_save(request, form, form_instance)

            form.save_m2m()  # save payment methods
            formset.save()  # save price options

            # remove all pricings if no custom_payment form
            if not form.cleaned_data['custom_payment']:
                form_instance.pricing_set.all().delete()

            messages.add_message(request, messages.SUCCESS, 'Successfully edited %s' % form_instance)
            return HttpResponseRedirect(reverse('form_field_update', args=[form_instance.pk]))
    else:
        form = form_class(instance=form_instance, user=request.user)
        if form_instance.recurring_payment:
            formset = RecurringPaymentFormSet(instance=form_instance)
        else:
            formset = PricingFormSet(instance=form_instance)
    return render_to_response(template_name, {
        'form':form,
        'formset':formset,
        'form_instance':form_instance,
        },context_instance=RequestContext(request))


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
            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % form_instance)
            return redirect('form_detail', form_instance.slug)
    else:
        form = form_class(instance=form_instance, queryset=form_instance.fields.all().order_by('position'))

    return render_to_response(template_name, {'form':form, 'form_instance':form_instance},
        context_instance=RequestContext(request))


@is_enabled('forms')
@login_required
def delete(request, id, template_name="forms/delete.html"):
    form_instance = get_object_or_404(Form, pk=id)

    # check permission
    if not has_perm(request.user,'forms.delete_form',form_instance):
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % form_instance)

        form_instance.delete()
        return HttpResponseRedirect(reverse('forms'))

    return render_to_response(template_name, {'form': form_instance},
        context_instance=RequestContext(request))


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
            function_params = field.function_params,
            required = field.required,
            visible = field.visible,
            choices = field.choices,
            position = field.position,
            default = field.default,
            )

    EventLog.objects.log(instance=form_instance)
    messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % new_form)
    return redirect('form_edit', new_form.pk)


@is_enabled('forms')
@login_required
def entries(request, id, template_name="forms/entries.html"):
    form = get_object_or_404(Form, pk=id)

    if not has_perm(request.user,'forms.change_form',form):
        raise Http403

    entries = form.entries.all()

    EventLog.objects.log(instance=form)

    return render_to_response(template_name, {'form':form,'entries': entries},
        context_instance=RequestContext(request))


@is_enabled('forms')
@login_required
def entry_delete(request, id, template_name="forms/entry_delete.html"):
    entry = get_object_or_404(FormEntry, pk=id)

    # check permission
    if not has_perm(request.user,'forms.delete_form',entry.form):
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted entry %s' % entry)
        entry.delete()
        return HttpResponseRedirect(reverse('forms'))

    return render_to_response(template_name, {'entry': entry},
        context_instance=RequestContext(request))


@is_enabled('forms')
@login_required
def entry_detail(request, id, template_name="forms/entry_detail.html"):
    entry = get_object_or_404(FormEntry, pk=id)

    # check permission
    if not has_perm(request.user,'forms.change_form',entry.form):
        raise Http403

    return render_to_response(template_name, {'entry':entry},
        context_instance=RequestContext(request))


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
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=export_entries_%d.csv' % time()
        writer = csv.writer(response, delimiter=',')

    return response

def entries_export_status(request, task_id, template_name="forms/entry_export_status.html"):
    try:
        task = TaskMeta.objects.get(task_id=task_id)
    except TaskMeta.DoesNotExist:
        task = None
        
    return render_to_response(template_name, {
        'task':task,
        'task_id':task_id,
        'user_this':None,
    }, context_instance=RequestContext(request))
    
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
        forms = forms.filter(Q(title__icontains=query)|Q(intro__icontains=query)|Q(response__icontains=query))

    forms = forms.order_by('-pk')

    EventLog.objects.log()

    return render_to_response(template_name, {'forms':forms},
        context_instance=RequestContext(request))


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
    if form.recurring_payment and request.user.is_anonymous():
        response = redirect('auth_login')
        response['Location'] += '?next=%s' % form.get_absolute_url()
        return response

    form_for_form = FormForForm(form, request.user, request.POST or None, request.FILES or None)

    for field in form_for_form.fields:
        field_default = request.GET.get(field, None)
        if field_default:
            form_for_form.fields[field].initial = field_default

    if request.method == "POST":
        if form_for_form.is_valid():
            entry = form_for_form.save()
            entry.entry_path = request.POST.get("entry_path", "")
            if request.user.is_anonymous():
                if entry.get_email_address():
                    emailfield = entry.get_email_address()
                    firstnamefield = entry.get_first_name()
                    lastnamefield = entry.get_last_name()
                    phonefield = entry.get_phone_number()
                    password = ''
                    for i in range(0, 10):
                        password += random.choice(string.ascii_lowercase + string.ascii_uppercase)

                    user_list = User.objects.filter(email=emailfield).order_by('-last_login')
                    if user_list:
                        anonymous_creator = user_list[0]
                    else:
                        anonymous_creator = User(username=emailfield[:30], email=emailfield, 
                                                 first_name=firstnamefield, last_name=lastnamefield)
                        anonymous_creator.set_password(password)
                        anonymous_creator.is_active = False
                        anonymous_creator.save()
                        anonymous_profile = Profile(user=anonymous_creator, owner=anonymous_creator,
                                                    creator=anonymous_creator, phone=phonefield)
                        anonymous_profile.save()
                    entry.creator = anonymous_creator
            else:
                entry.creator = request.user
            entry.save()

            # Email
            subject = generate_email_subject(form, entry)
            email_headers = {}  # content type specified below
            if form.email_from:
                email_headers.update({'Reply-To':form.email_from})

            # Email to submitter
            # fields aren't included in submitter body to prevent spam
            submitter_body = generate_submitter_email_body(entry, form_for_form)
            email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
            sender = get_setting('site', 'global', 'siteemailnoreplyaddress')
            email_to = form_for_form.email_to()
            if email_to and form.send_email and form.email_text:
                # Send message to the person who submitted the form.
                msg = EmailMessage(subject, submitter_body, sender, [email_to], headers=email_headers)
                msg.content_subtype = 'html'

                try:
                    msg.send(fail_silently=True)
                except:
                    pass

            # Email copies to admin
            admin_body = generate_admin_email_body(entry, form_for_form)
            email_from = email_to or email_from # Send from the email entered.
            email_headers = {}  # Reset the email_headers
            email_headers.update({'Reply-To':email_from})
            email_copies = [e.strip() for e in form.email_copies.split(",")
                if e.strip()]
            if email_copies:
                # Send message to the email addresses listed in the copies.
                msg = EmailMessage(subject, admin_body, sender, email_copies, headers=email_headers)
                msg.content_subtype = 'html'
                for f in form_for_form.files.values():
                    try:
                        f.open()
                        f.seek(0)
                        msg.attach(f.name, f.read())
                        f.close()
                    except Exception:
                        pass

                try:
                    msg.send(fail_silently=True)
                except:
                    pass

            # payment redirect
            if (form.custom_payment or form.recurring_payment) and entry.pricing:
                # get the pricing's price, custom or otherwise
                price = entry.pricing.price or form_for_form.cleaned_data.get('custom_price')

                if form.recurring_payment:
                    billing_start_dt = datetime.datetime.now()
                    trial_period_start_dt = None
                    trial_period_end_dt = None
                    if entry.pricing.has_trial_period:
                        trial_period_start_dt = datetime.datetime.now()
                        trial_period_end_dt = trial_period_start_dt + datetime.timedelta(1)
                        billing_start_dt = trial_period_end_dt
                    # Create recurring payment
                    rp = RecurringPayment(
                             user=request.user,
                             description=entry.pricing.label,
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
                             creator=request.user,
                             creator_username=request.user.username,
                             owner=request.user,
                             owner_username=request.user.username,
                         )
                    rp.save()
                    rp.add_customer_profile()

                    # redirect to recurring payments
                    messages.add_message(request, messages.SUCCESS, 'Successful transaction.')
                    return redirect('recurring_payment.my_accounts')
                else:
                    # create the invoice
                    invoice = make_invoice_for_entry(entry, custom_price=price)
                    # log an event for invoice add

                    EventLog.objects.log(instance=form)

                    # redirect to billing form
                    return redirect('form_entry_payment', invoice.id, invoice.guid)

            # default redirect
            if form.completion_url:
                return redirect(form.completion_url)
            return redirect("form_sent", form.slug)
    # set form's template to default if no template or template doesn't exist
    if not form.template or not template_exists(form.template):
        form.template = "default.html"
    context = {
        "form": form,
        "form_for_form": form_for_form,
        'form_template': form.template,
    }
    return render_to_response(template, context, RequestContext(request))

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
    return render_to_response(template, context, RequestContext(request))


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
        if request.user.is_authenticated():
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
    return render_to_response(template, {
            'payment_form':form,
            'form':entry.form,
            'form_template': form_template,
        }, context_instance=RequestContext(request))


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

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))


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
    from django.http import Http404
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage
    from tendenci.core.perms.utils import has_view_perm
    from tendenci.apps.forms_builder.forms.models import FieldEntry

    field = get_object_or_404(FieldEntry, pk=id)
    form = field.field.form

    base_name = os.path.basename(field.value)
    mime_type = mimetypes.guess_type(base_name)[0]

    if not has_view_perm(request.user, 'forms.view_form', form):
        raise Http403

    if not mime_type:
        raise Http404

    if not default_storage.exists(field.value):
        raise Http404

    data = default_storage.open(field.value).read()
    f = ContentFile(data)

    EventLog.objects.log()
    response = HttpResponse(f.read(), mimetype=mime_type)
    response['Content-Disposition'] = 'filename=%s' % base_name
    return response
