from builtins import str
from datetime import timedelta, datetime
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.http import Http404

from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (
    get_notice_recipients,
    update_perms_and_save,
    has_perm,
    get_query_filters,
    has_view_perm)
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task
from tendenci.apps.jobs.models import Job, JobPricing
from tendenci.apps.jobs.models import Category as JobCategory
from tendenci.apps.jobs.forms import JobForm, JobPricingForm, JobSearchForm
from tendenci.apps.jobs.utils import is_free_listing, job_set_inv_payment

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None
from tendenci.apps.base.utils import send_email_notification


@is_enabled('jobs')
def detail(request, slug=None, template_name="jobs/view.html"):
    if not slug:
        return HttpResponseRedirect(reverse('jobs'))
    job = get_object_or_404(Job.objects.select_related(), slug=slug)

    can_view = has_view_perm(request.user, 'jobs.view_job', job)

    if can_view:
        EventLog.objects.log(instance=job)
        return render_to_resp(request=request, template_name=template_name,
            context={'job': job})
    else:
        raise Http403


@is_enabled('jobs')
def search(request, template_name="jobs/search.html"):
    query = request.GET.get('q', None)
    my_pending_jobs = request.GET.get('my_pending_jobs', False)

    filters = get_query_filters(request.user, 'jobs.view_job')
    jobs = Job.objects.filter(filters).distinct()
    if not request.user.is_anonymous:
        jobs = jobs.select_related()

    form = JobSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('q')
        cat = form.cleaned_data.get('cat')
        sub_cat = form.cleaned_data.get('sub_cat')

        if cat:
            jobs = jobs.filter(cat=cat)
        if sub_cat:
            jobs = jobs.filter(sub_cat=sub_cat)
        if query:
            if 'tag:' in query:
                tag = query.strip('tag:')
                jobs = jobs.filter(tags__icontains=tag)
            else:
                jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        # filter out expired and not activated
        if not has_perm(request.user, 'jobs.change_job'):
            jobs = jobs.filter(activation_dt__lte=datetime.now(), expiration_dt__gt=datetime.now())
    else:
        jobs = Job.objects.none()

    # filter for "my pending jobs"
    if my_pending_jobs and not request.user.is_anonymous:
        template_name = "jobs/my_pending_jobs.html"
        jobs = jobs.filter(
            creator_username=request.user.username,
            status_detail__contains='pending'
        )

    jobs = jobs.order_by('list_type', '-post_dt', '-update_dt')

    EventLog.objects.log()

    return render_to_resp(
        request=request, template_name=template_name,
        context={'jobs': jobs, 'form': form}
    )


def search_redirect(request):
    return HttpResponseRedirect(reverse('jobs'))


@is_enabled('jobs')
def my_jobs(request, template_name = "jobs/my_jobs.html"):
    query = request.GET.get('q', None)
    if not request.user.is_anonymous:
        if get_setting('site', 'global', 'searchindex') and query:
            jobs = Job.objects.search(query, user=request.user)
            jobs = jobs.order_by('-post_dt')
        else:
            filters = get_query_filters(request.user, 'jobs.view_job')
            jobs = Job.objects.filter(filters).distinct()
            jobs = jobs.select_related()
            jobs = jobs.order_by('status_detail', 'list_type', '-post_dt')
        jobs = jobs.filter(creator_username=request.user.username)

        EventLog.objects.log()

        return render_to_resp(request=request, template_name=template_name,
            context={'jobs': jobs})
    else:
        return HttpResponseRedirect(reverse('jobs'))


@is_enabled('jobs')
def print_view(request, slug, template_name="jobs/print-view.html"):
    job = get_object_or_404(Job, slug=slug)

    can_view = has_view_perm(request.user, 'jobs.view_job', job)

    if can_view:
        EventLog.objects.log(instance=job)

        return render_to_resp(request=request, template_name=template_name,
            context={'job': job})
    else:
        raise Http403


@is_enabled('jobs')
@login_required
def add(request, form_class=JobForm, template_name="jobs/add.html",
        object_type=Job, success_redirect='job', thankyou_redirect='job.thank_you'):

    require_payment = get_setting('module', 'jobs',
                                    'jobsrequirespayment')

    can_add_active = has_perm(request.user, 'jobs.add_job')

    get_object_or_404(
        ContentType,
        app_label=object_type._meta.app_label,
        model=object_type._meta.model_name
    )

    form = form_class(request.POST or None, request.FILES or None, user=request.user)
    # adjust the fields depending on user type
    if not require_payment:
        del form.fields['payment_method']
        del form.fields['list_type']

    if request.method == "POST":
        if require_payment:
            is_free = is_free_listing(request.user,
                               request.POST.get('pricing', 0),
                               request.POST.get('list_type'))
            if is_free:
                del form.fields['payment_method']

        if form.is_valid():
            job = form.save(commit=False)
            pricing = form.cleaned_data['pricing']

            if require_payment and is_free:
                job.payment_method = 'paid - cc'

            # set it to pending if the user is anonymous or not an admin
            if not can_add_active:
                #job.status = 1
                job.status_detail = 'pending'

            # list types and duration
            if not job.requested_duration:
                job.requested_duration = 30
            if not job.list_type:
                job.list_type = 'regular'

            # set up all the times
            now = datetime.now()
            job.activation_dt = now
            if not job.post_dt:
                job.post_dt = now

            # set the expiration date
            job.expiration_dt = job.activation_dt + timedelta(
                                        days=job.requested_duration)

            # semi-anon job posts don't get a slug field on the form
            # see __init__ method in JobForm
            if not job.slug:
                #job.slug = get_job_unique_slug(slugify(job.title))
                job.slug = '%s-%s' % (slugify(job.title),
                                        object_type.objects.count())

            job = update_perms_and_save(request, form, job)

            # create invoice
            job_set_inv_payment(request.user, job, pricing)

            #save relationships
            job.save()
            msg_string = u'Successfully added %s' % str(job)
            messages.add_message(request, messages.SUCCESS,_(msg_string))

            # send notification to administrators
            recipients = get_notice_recipients(
                            'module', 'jobs', 'jobrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send_emails(recipients, 'job_added',
                                                extra_context)

            # send user to the payment page if payment is required
            if require_payment:
                if job.payment_method.lower() in ['credit card', 'cc', 'online payment']:
                    if job.invoice and job.invoice.balance > 0:
                        return HttpResponseRedirect(reverse(
                            'payment.pay_online',
                            args=[job.invoice.id, job.invoice.guid])
                        )

            # send user to thank you or view page
            if request.user.profile.is_superuser:
                return HttpResponseRedirect(
                        reverse(success_redirect, args=[job.slug]))
            else:
                return HttpResponseRedirect(reverse(thankyou_redirect))
    else:
        # Redirect user w/perms to create pricing if none exist
        pricings = JobPricing.objects.all()
        if not pricings and has_perm(request.user, 'jobs.add_jobpricing'):
            msg_string = 'You need to add a %s Pricing before you can add a %s.' % (get_setting('module', 'jobs', 'label_plural'),get_setting('module', 'jobs', 'label'))
            messages.add_message(request, messages.WARNING, _(msg_string))
            return HttpResponseRedirect(reverse('job_pricing.add'))

    return render_to_resp(request=request, template_name=template_name,
            context={'form': form,
             'require_payment': require_payment})


@csrf_exempt
@login_required
def query_price(request):
    """
    Get the price for user with the selected list type.
    """
    pricing_id = request.POST.get('pricing_id', 0)
    list_type = request.POST.get('list_type', '')
    pricing = get_object_or_404(JobPricing, pk=pricing_id)
    price = pricing.get_price_for_user(request.user, list_type=list_type)
    return HttpResponse(simplejson.dumps({'price': price}))


@is_enabled('jobs')
@login_required
def edit(request, id, form_class=JobForm, template_name="jobs/edit.html", object_type=Job, success_redirect='job', job_change_perm='jobs.change_job'):
    job = get_object_or_404(object_type, pk=id)

    if not has_perm(request.user, job_change_perm, job):
        raise Http403

    form = form_class(request.POST or None,
                        instance=job,
                        user=request.user)

    # delete admin only fields for non-admin on edit - GJQ 8/25/2010
    if not request.user.profile.is_superuser:
        del form.fields['pricing']
        del form.fields['list_type']
        if 'activation_dt' in form.fields:
            del form.fields['activation_dt']
        if 'post_dt' in form.fields:
            del form.fields['post_dt']
        if 'expiration_dt' in form.fields:
            del form.fields['expiration_dt']
        if 'entity' in form.fields:
            del form.fields['entity']
    del form.fields['payment_method']

    if request.method == "POST":
        if form.is_valid():
            job = form.save(commit=False)

            job = update_perms_and_save(request, form, job)

            msg_string = u'Successfully updated {}'.format(str(job))
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(
                reverse(success_redirect, args=[job.slug]))

    return render_to_resp(request=request, template_name=template_name, context={
        'job': job,
        'form': form,
        })


@is_enabled('jobs')
@login_required
def get_subcategories(request):
    if request.is_ajax() and request.method == "POST":
        category = request.POST.get('category', None)
        if category:
            sub_categories = JobCategory.objects.filter(parent=category)
            count = sub_categories.count()
            sub_categories = list(sub_categories.values_list('pk','name'))
            data = json.dumps({"error": False,
                               "sub_categories": sub_categories,
                               "count": count})
        else:
            data = json.dumps({"error": True})

        return HttpResponse(data, content_type="text/plain")
    raise Http404


@is_enabled('jobs')
@login_required
def edit_meta(request, id, form_class=MetaForm,
                    template_name="jobs/edit-meta.html"):

    # check permission
    job = get_object_or_404(Job, pk=id)
    if not has_perm(request.user, 'jobs.change_job', job):
        raise Http403

    defaults = {
        'title': job.get_title(),
        'description': job.get_description(),
        'keywords': job.get_keywords(),
        'canonical_url': job.get_canonical_url(),
    }
    job.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=job.meta)
        if form.is_valid():
            job.meta = form.save()  # save meta
            job.save()  # save relationship
            msg_string = u'Successfully updated meta for {}'.format(str(job))
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            return HttpResponseRedirect(reverse('job', args=[job.slug]))
    else:
        form = form_class(instance=job.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'job': job, 'form': form})


@is_enabled('jobs')
@login_required
def delete(request, id, template_name="jobs/delete.html"):
    job = get_object_or_404(Job, pk=id)

    if has_perm(request.user, 'jobs.delete_job', job):
        if request.method == "POST":
            msg_string = u'Successfully deleted {}'.format(str(job))
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            # send notification to administrators
            recipients = get_notice_recipients(
                            'module', 'jobs', 'jobrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send_emails(recipients,
                        'job_deleted', extra_context)

            job.delete()

            return HttpResponseRedirect(reverse('job.search'))

        return render_to_resp(request=request, template_name=template_name,
            context={'job': job})
    else:
        raise Http403


@is_enabled('jobs')
@login_required
def pricing_add(request, form_class=JobPricingForm,
                    template_name="jobs/pricing-add.html"):

    if has_perm(request.user, 'jobs.add_jobpricing'):
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                job_pricing = form.save(commit=False)
                job_pricing.status = 1
                job_pricing.save(request.user)

                EventLog.objects.log(instance=job_pricing)

                if "_popup" in request.POST:
                    return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % (escape(job_pricing.pk), escape(job_pricing)))

                return HttpResponseRedirect(
                    reverse('job_pricing.view', args=[job_pricing.id]))
        else:
            form = form_class()

        if "_popup" in request.GET:
            template_name="jobs/pricing-add-popup.html"

        return render_to_resp(request=request, template_name=template_name,
            context={'form': form})
    else:
        raise Http403


@is_enabled('jobs')
@login_required
def pricing_edit(request, id, form_class=JobPricingForm,
                    template_name="jobs/pricing-edit.html"):
    job_pricing = get_object_or_404(JobPricing, pk=id)
    if not has_perm(request.user, 'jobs.change_jobpricing', job_pricing):
        Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=job_pricing)
        if form.is_valid():
            job_pricing = form.save(commit=False)
            job_pricing.save(request.user)

            EventLog.objects.log(instance=job_pricing)

            return HttpResponseRedirect(reverse(
                'job_pricing.view',
                args=[job_pricing.id])
            )
    else:
        form = form_class(instance=job_pricing)

    return render_to_resp(request=request, template_name=template_name,
        context={'form': form})


@is_enabled('jobs')
@login_required
def pricing_view(request, id, template_name="jobs/pricing-view.html"):
    job_pricing = get_object_or_404(JobPricing, id=id)

    if has_perm(request.user, 'jobs.view_jobpricing', job_pricing):
        EventLog.objects.log(instance=job_pricing)
        return render_to_resp(request=request, template_name=template_name,
            context={'job_pricing': job_pricing})
    else:
        raise Http403


@is_enabled('jobs')
@login_required
def pricing_delete(request, id, template_name="jobs/pricing-delete.html"):
    job_pricing = get_object_or_404(JobPricing, pk=id)

    if not has_perm(request.user, 'jobs.delete_jobpricing'):
        raise Http403

    if request.method == "POST":
        EventLog.objects.log(instance=job_pricing)
        messages.add_message(request, messages.SUCCESS,
            'Successfully deleted %s' % job_pricing)

        job_pricing.delete()

        return HttpResponseRedirect(reverse('job_pricing.search'))

    return render_to_resp(request=request, template_name=template_name,
        context={'job_pricing': job_pricing})


@is_enabled('jobs')
def pricing_search(request, template_name="jobs/pricing-search.html"):
    job_pricings = JobPricing.objects.all().order_by('duration')

    EventLog.objects.log()
    return render_to_resp(request=request, template_name=template_name,
        context={'job_pricings': job_pricings})


@is_enabled('jobs')
@login_required
def pending(request, template_name="jobs/pending.html"):
    can_view_jobs = has_perm(request.user, 'jobs.view_job')
    can_change_jobs = has_perm(request.user, 'jobs.change_job')

    if not all([can_view_jobs, can_change_jobs]):
        raise Http403

    EventLog.objects.log()
    jobs = Job.objects.filter(status_detail__contains='pending')
    return render_to_resp(request=request, template_name=template_name,
            context={'jobs': jobs})


@login_required
def approve(request, id, template_name="jobs/approve.html"):
    can_view_jobs = has_perm(request.user, 'jobs.view_job')
    can_change_jobs = has_perm(request.user, 'jobs.change_job')

    if not all([can_view_jobs, can_change_jobs]):
        raise Http403

    job = get_object_or_404(Job, pk=id)

    if request.method == "POST":
        job.activation_dt = datetime.now()
        job.allow_anonymous_view = True
        job.status = True
        job.status_detail = 'active'

        if not job.creator:
            job.creator = request.user
            job.creator_username = request.user.username

        if not job.owner:
            job.owner = request.user
            job.owner_username = request.user.username

        job.save()

        # send email notification to user
        recipients = [job.creator.email]
        if recipients:
            extra_context = {
                'object': job,
                'request': request,
            }
            #try:
            send_email_notification(
                'job_approved_user_notice', recipients, extra_context)
            #except:
            #    pass
        msg_string = u'Successfully approved {}'.format(str(job))
        messages.add_message(request, messages.SUCCESS, _(msg_string))

        return HttpResponseRedirect(reverse('job', args=[job.slug]))

    return render_to_resp(request=request, template_name=template_name,
            context={'job': job})


def thank_you(request, template_name="jobs/thank-you.html"):
    return render_to_resp(request=request, template_name=template_name)


@is_enabled('jobs')
@login_required
def export(request, template_name="jobs/export.html"):
    """Export Jobs"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        fields = [
            'guid',
            'title',
            'slug',
            'description',
            'list_type',
            'code',
            'location',
            'skills',
            'experience',
            'education',
            'level',
            'period',
            'is_agency',
            'contact_method',
            'position_reports_to',
            'salary_from',
            'salary_to',
            'computer_skills',
            'requested_duration',
            'pricing',
            'activation_dt',
            'post_dt',
            'expiration_dt',
            'start_dt',
            'job_url',
            'syndicate',
            'design_notes',
            'contact_company',
            'contact_name',
            'contact_address',
            'contact_address2',
            'contact_city',
            'contact_state',
            'contact_zip_code',
            'contact_country',
            'contact_phone',
            'contact_fax',
            'contact_email',
            'contact_website',
            'meta',
            'entity',
            'tags',
            'invoice',
            'payment_method',
            'member_price',
            'member_count',
            'non_member_price',
            'non_member_count',
        ]
        export_id = run_export_task('jobs', 'job', fields)
        EventLog.objects.log()
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
