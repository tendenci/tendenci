from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from base.http import Http403
from base.utils import now_localized
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from site_settings.utils import get_setting
from perms.utils import (get_notice_recipients, is_admin, is_developer,
    update_perms_and_save, is_member, has_perm, get_query_filters,
    has_view_perm)
from categories.forms import CategoryForm, CategoryForm2
from categories.models import Category
from theme.shortcuts import themed_response as render_to_response
from exports.tasks import TendenciExportTask

from jobs.models import Job, JobPricing
from jobs.forms import JobForm, JobPricingForm
from jobs.utils import job_set_inv_payment, get_job_unique_slug

try:
    from notification import models as notification
except:
    notification = None
from base.utils import send_email_notification


def details(request, slug=None, template_name="jobs/view.html"):
    if not slug:
        return HttpResponseRedirect(reverse('jobs'))
    job = get_object_or_404(Job.objects.select_related(), slug=slug)

    can_view = has_view_perm(request.user, 'jobs.view_job', job)

    if can_view:
        log_defaults = {
            'event_id': 255000,
            'event_data': '%s (%d) viewed by %s' % (
                 job._meta.object_name,
                 job.pk, request.user
            ),
            'description': '%s viewed' % job._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': job,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'job': job},
            context_instance=RequestContext(request))
    else:
        raise Http403


def search(request, template_name="jobs/search.html"):
    query = request.GET.get('q', None)
    my_jobs = request.GET.get('my_jobs', False)
    
    if get_setting('site', 'global', 'searchindex') and query:
        jobs = Job.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'jobs.view_job')
        jobs = Job.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            jobs = jobs.select_related()
    
    jobs = jobs.order_by('status_detail','list_type','-post_dt')
    
    # filter for "my jobs"
    if my_jobs and not request.user.is_anonymous():
        template_name = "jobs/my_jobs.html"
        jobs = jobs.filter(creator_username=request.user.username)
    
    log_defaults = {
        'event_id': 254000,
        'event_data': '%s searched by %s' % ('Job', request.user),
        'description': '%s searched' % 'Job',
        'user': request.user,
        'request': request,
        'source': 'jobs'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_response(template_name, {'jobs': jobs},
        context_instance=RequestContext(request))


def search_redirect(request):
    return HttpResponseRedirect(reverse('jobs'))


def print_view(request, slug, template_name="jobs/print-view.html"):
    job = get_object_or_404(Job, slug=slug)

    can_view = has_view_perm(request.user, 'jobs.view_job', job)

    if can_view:
        log_defaults = {
            'event_id': 255001,
            'event_data': '%s (%d) viewed by %s' % (job._meta.object_name, job.pk, request.user),
            'description': '%s viewed - print view' % job._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': job,
        }
        EventLog.objects.log(**log_defaults)

        return render_to_response(template_name, {'job': job},
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=JobForm, template_name="jobs/add.html"):
    require_payment = get_setting('module', 'jobs', 'jobsrequirespayment')
    
    can_add_active = has_perm(request.user, 'jobs.add_job')
    
    content_type = get_object_or_404(ContentType, app_label='jobs',model='job')
    
    if is_admin(request.user):
        category_form_class = CategoryForm
    else:
        category_form_class = CategoryForm2
    
    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        categoryform = category_form_class(
                        content_type, 
                        request.POST,
                        prefix='category')

        # adjust the fields depending on user type
        if not require_payment:
            del form.fields['payment_method']
            del form.fields['list_type']

        if form.is_valid() and categoryform.is_valid():
            job = form.save(commit=False)
            pricing = form.cleaned_data['pricing']

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
            now = now_localized()
            job.activation_dt = now
            if not job.post_dt:
                job.post_dt = now

            # set the expiration date
            job.expiration_dt = job.activation_dt + timedelta(days=job.requested_duration)
            
            # semi-anon job posts don't get a slug field on the form
            # see __init__ method in JobForm
            if not job.slug:
                #job.slug = get_job_unique_slug(slugify(job.title))
                job.slug = '%s-%s' % (slugify(job.title), Job.objects.count())

            job = update_perms_and_save(request, form, job)

            # create invoice
            job_set_inv_payment(request.user, job, pricing)
            
            #setup categories
            category = Category.objects.get_for_object(job,'category')
            sub_category = Category.objects.get_for_object(job,'sub_category')
            
            ## update the category of the job
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0': 
                Category.objects.update(job,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(job,'category')
                Category.objects.remove(job,'sub_category')
            
            if not category_removed:
                # update the sub category of the job
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0': 
                    Category.objects.update(job, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(job,'sub_category') 
            
            #save relationships
            job.save()
            
            log_defaults = {
                'event_id': 251000,
                'event_data': '%s (%d) added by %s' % (job._meta.object_name, job.pk, request.user),
                'description': '%s added' % job._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job,
            }
            EventLog.objects.log(**log_defaults)

            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % job)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'jobs', 'jobrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send_emails(recipients, 'job_added', extra_context)

            # send user to the payment page if payment is required
            if require_payment:
                if job.payment_method.lower() in ['credit card', 'cc']:
                    if job.invoice and job.invoice.balance > 0:
                        return HttpResponseRedirect(reverse(
                            'payments.views.pay_online',
                            args=[job.invoice.id, job.invoice.guid])
                        )

            # send user to thank you or view page
            if is_admin(request.user):
                return HttpResponseRedirect(reverse('job', args=[job.slug]))
            else:
                return HttpResponseRedirect(reverse('job.thank_you'))
    else:
        # Redirect user w/perms to create pricing if none exist
        pricings = JobPricing.objects.all()
        if not pricings and has_perm(request.user, 'jobs.add_jobpricing'):
            messages.add_message(request, messages.WARNING, 'You need to add a %s Pricing before you can add a %s.' % (get_setting('module', 'jobs', 'label_plural'),get_setting('module', 'jobs', 'label')))
            return HttpResponseRedirect(reverse('job_pricing.add'))

        form = form_class(user=request.user)
        initial_category_form_data = {
            'app_label': 'jobs',
            'model': 'job',
            'pk': 0, #not used for this view but is required for the form
        }
        categoryform = category_form_class(
                        content_type,
                        initial=initial_category_form_data,
                        prefix='category')
        
        # adjust the fields depending on user type
        if not require_payment:
            del form.fields['payment_method']
            del form.fields['list_type']
    
    return render_to_response(template_name, 
            {'form': form, 'categoryform':categoryform},
            context_instance=RequestContext(request))


@login_required
def edit(request, id, form_class=JobForm, template_name="jobs/edit.html"):
    job = get_object_or_404(Job, pk=id)
    
    if not has_perm(request.user, 'jobs.change_job', job):
        raise Http403
        
    form = form_class(request.POST or None,
                        instance=job,
                        user=request.user)
    
    #setup categories
    content_type = get_object_or_404(ContentType, app_label='jobs',model='job')
    category = Category.objects.get_for_object(job,'category')
    sub_category = Category.objects.get_for_object(job,'sub_category')
    initial_category_form_data = {
        'app_label': 'jobs',
        'model': 'job',
        'pk': job.pk,
        'category': getattr(category,'name','0'),
        'sub_category': getattr(sub_category,'name','0')
    }
    if is_admin(request.user):
        category_form_class = CategoryForm
    else:
        category_form_class = CategoryForm2
    categoryform = category_form_class(
                        content_type, 
                        request.POST or None,
                        initial= initial_category_form_data,
                        prefix='category')
    
    # delete admin only fields for non-admin on edit - GJQ 8/25/2010
    if not is_admin(request.user):
        del form.fields['pricing']
        del form.fields['list_type']
        if form.fields.has_key('activation_dt'):
            del form.fields['activation_dt']
        if form.fields.has_key('post_dt'):
            del form.fields['post_dt']
        if form.fields.has_key('expiration_dt'):
            del form.fields['expiration_dt']
        if form.fields.has_key('entity'):
            del form.fields['entity']
    del form.fields['payment_method']
    
    if request.method == "POST":
        if form.is_valid() and categoryform.is_valid():
            job = form.save(commit=False)

            job = update_perms_and_save(request, form, job)
            
            ## update the category of the job
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0': 
                Category.objects.update(job ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(job ,'category')
                Category.objects.remove(job ,'sub_category')
            
            if not category_removed:
                # update the sub category of the job
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0': 
                    Category.objects.update(job, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(job,'sub_category')
                    
            #save relationships
            job.save()

            log_defaults = {
                'event_id': 252000,
                'event_data': '%s (%d) edited by %s' % (job._meta.object_name, job.pk, request.user),
                'description': '%s edited' % job._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job,
            }
            EventLog.objects.log(**log_defaults)

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % job)

            return HttpResponseRedirect(reverse('job', args=[job.slug]))

    return render_to_response(template_name,
                {'job': job, 'form': form, 'categoryform':categoryform},
                context_instance=RequestContext(request))
    


@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="jobs/edit-meta.html"):

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

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % job)

            return HttpResponseRedirect(reverse('job', args=[job.slug]))
    else:
        form = form_class(instance=job.meta)

    return render_to_response(template_name, {'job': job, 'form': form},
        context_instance=RequestContext(request))


@login_required
def delete(request, id, template_name="jobs/delete.html"):
    job = get_object_or_404(Job, pk=id)

    if has_perm(request.user, 'jobs.delete_job', job):
        if request.method == "POST":
            log_defaults = {
                'event_id': 433000,
                'event_data': '%s (%d) deleted by %s' % (job._meta.object_name, job.pk, request.user),
                'description': '%s deleted' % job._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job,
            }

            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % job)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'jobs', 'jobrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send_emails(recipients, 'job_deleted', extra_context)

            job.delete()

            return HttpResponseRedirect(reverse('job.search'))

        return render_to_response(template_name, {'job': job},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def pricing_add(request, form_class=JobPricingForm, template_name="jobs/pricing-add.html"):
    if has_perm(request.user, 'jobs.add_jobpricing'):
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                job_pricing = form.save(commit=False)
                job_pricing.status = 1
                job_pricing.save(request.user)

                log_defaults = {
                    'event_id': 265100,
                    'event_data': '%s (%d) added by %s' % (
                        job_pricing._meta.object_name,
                        job_pricing.pk,
                        request.user
                    ),
                    'description': '%s added' % job_pricing._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': job_pricing,
                }
                EventLog.objects.log(**log_defaults)

                return HttpResponseRedirect(reverse('job_pricing.view', args=[job_pricing.id]))
        else:
            form = form_class()

        return render_to_response(template_name, {'form': form},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def pricing_edit(request, id, form_class=JobPricingForm, template_name="jobs/pricing-edit.html"):
    job_pricing = get_object_or_404(JobPricing, pk=id)
    if not has_perm(request.user, 'jobs.change_jobpricing', job_pricing):
        Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=job_pricing)
        if form.is_valid():
            job_pricing = form.save(commit=False)
            job_pricing.save(request.user)

            log_defaults = {
                'event_id': 265110,
                'event_data': '%s (%d) edited by %s' % (
                    job_pricing._meta.object_name,
                    job_pricing.pk,
                    request.user
                ),
                'description': '%s edited' % job_pricing._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job_pricing,
            }
            EventLog.objects.log(**log_defaults)

            return HttpResponseRedirect(reverse(
                'job_pricing.view',
                args=[job_pricing.id])
            )
    else:
        form = form_class(instance=job_pricing)

    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))


@login_required
def pricing_view(request, id, template_name="jobs/pricing-view.html"):
    job_pricing = get_object_or_404(JobPricing, id=id)

    if has_perm(request.user, 'jobs.view_jobpricing', job_pricing):
        return render_to_response(template_name, {'job_pricing': job_pricing},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def pricing_delete(request, id, template_name="jobs/pricing-delete.html"):
    job_pricing = get_object_or_404(JobPricing, pk=id)

    if not has_perm(request.user, 'jobs.delete_jobpricing'):
        raise Http403

    if request.method == "POST":
        log_defaults = {
            'event_id': 265120,
            'event_data': '%s (%d) deleted by %s' % (
                job_pricing._meta.object_name,
                job_pricing.pk,
                request.user
            ),
            'description': '%s deleted' % job_pricing._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': job_pricing,
        }

        EventLog.objects.log(**log_defaults)
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % job_pricing)

        job_pricing.delete()

        return HttpResponseRedirect(reverse('job_pricing.search'))

    return render_to_response(template_name, {'job_pricing': job_pricing},
        context_instance=RequestContext(request))


def pricing_search(request, template_name="jobs/pricing-search.html"):
    job_pricings = JobPricing.objects.all().order_by('duration')

    return render_to_response(template_name, {'job_pricings': job_pricings},
        context_instance=RequestContext(request))

@login_required
def pending(request, template_name="jobs/pending.html"):
    can_view_jobs = has_perm(request.user, 'jobs.view_job')
    can_change_jobs = has_perm(request.user, 'jobs.change_job')
    
    if not all([can_view_jobs, can_change_jobs]):
        raise Http403

    jobs = Job.objects.filter(status_detail__contains='pending')
    return render_to_response(template_name, {'jobs': jobs},
            context_instance=RequestContext(request))

@login_required
def approve(request, id, template_name="jobs/approve.html"):
    can_view_jobs = has_perm(request.user, 'jobs.view_job')
    can_change_jobs = has_perm(request.user, 'jobs.change_job')
    
    if not all([can_view_jobs, can_change_jobs]):
        raise Http403
    
    job = get_object_or_404(Job, pk=id)

    if request.method == "POST":
        job.activation_dt = now_localized()
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
            send_email_notification('job_approved_user_notice', recipients, extra_context)
            #except:
            #    pass

        messages.add_message(request, messages.SUCCESS, 'Successfully approved %s' % job)

        return HttpResponseRedirect(reverse('job', args=[job.slug]))

    return render_to_response(template_name, {'job': job},
            context_instance=RequestContext(request))


def thank_you(request, template_name="jobs/thank-you.html"):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

@login_required
def export(request, template_name="jobs/export.html"):
    """Export Jobs"""
    
    if not is_admin(request.user):
        raise Http403
    
    if request.method == 'POST':
        # initilize initial values
        file_name = "jobs.xls"
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
            'percent_travel',
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
        
        if not settings.CELERY_IS_ACTIVE:
            # if celery server is not present 
            # evaluate the result and render the results page
            result = TendenciExportTask()
            response = result.run(Job, fields, file_name)
            return response
        else:
            result = TendenciExportTask.delay(Job, fields, file_name)
            return redirect('export.status', result.task_id)
        
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
