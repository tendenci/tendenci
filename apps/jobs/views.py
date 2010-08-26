from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from jobs.models import Job, JobPricing
from jobs.forms import JobForm, JobPricingForm
from jobs.utils import job_set_inv_payment
from perms.models import ObjectPermission
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm

from perms.utils import get_notice_recipients, is_admin


try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="jobs/view.html"):
    if not slug: return HttpResponseRedirect(reverse('job.search'))
    job = get_object_or_404(Job, slug=slug)
    
    if request.user.has_perm('jobs.view_job', job):
        log_defaults = {
            'event_id' : 255000,
            'event_data': '%s (%d) viewed by %s' % (job._meta.object_name, job.pk, request.user),
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
    jobs = Job.objects.search(query, user=request.user)

    log_defaults = {
        'event_id' : 254000,
        'event_data': '%s searched by %s' % ('Job', request.user),
        'description': '%s searched' % 'Job',
        'user': request.user,
        'request': request,
        'source': 'jobs'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'jobs':jobs}, 
        context_instance=RequestContext(request))

def print_view(request, slug, template_name="jobs/print-view.html"):
    job = get_object_or_404(Job, slug=slug)    

    log_defaults = {
        'event_id' : 255001,
        'event_data': '%s (%d) viewed by %s' % (job._meta.object_name, job.pk, request.user),
        'description': '%s viewed - print view' % job._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': job,
    }
    EventLog.objects.log(**log_defaults)
       
    if request.user.has_perm('jobs.view_job', job):
        return render_to_response(template_name, {'job': job}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def add(request, form_class=JobForm, template_name="jobs/add.html"):
    
    if not request.user.has_perm('jobs.add_job'): raise Http403
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if not is_admin(request.user):
            del form.fields['activation_dt']
            del form.fields['entity']
        del form.fields['post_dt']
        del form.fields['expiration_dt']
        
        if form.is_valid():           
            job = form.save(commit=False)
            # set up the user information
            job.creator = request.user
            job.creator_username = request.user.username
            job.owner = request.user
            job.owner_username = request.user.username
            job.save()
            
            if not job.requested_duration:
                job.requested_duration = 30
            if not job.list_type:
                job.list_type = 'regular'
            job.activation_dt = datetime.now()
            if not job.post_dt: job.post_dt = datetime.now()
            
            # set the expiration date
            job.expiration_dt = job.activation_dt + timedelta(days=job.requested_duration)
            
            if not job.status_detail: job.status_detail = 'Pending Approval'
            
    
            # assign permissions for selected users
            user_perms = form.cleaned_data['user_perms']
            if user_perms:
                ObjectPermission.objects.assign(user_perms, job)
            # assign creator permissions
            ObjectPermission.objects.assign(job.creator, job) 
    
            job.save() # update search-index w/ permissions
            
            # create invoice
            job_set_inv_payment(request.user, job)
    
            log_defaults = {
                'event_id' : 251000,
                'event_data': '%s (%d) added by %s' % (job._meta.object_name, job.pk, request.user),
                'description': '%s added' % job._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job,
            }
            EventLog.objects.log(**log_defaults)
    
            messages.add_message(request, messages.INFO, 'Successfully added %s' % job)
               
            # send notification to administrators
            recipients = get_notice_recipients('module', 'jobs', 'jobrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send_emails(recipients,'job_added', extra_context)
            
            if job.payment_method.lower() in ['credit card', 'cc']:
                if job.invoice and job.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payments.views.pay_online', args=[job.invoice.id, job.invoice.guid])) 
             
            return HttpResponseRedirect(reverse('job', args=[job.slug]))
    else:
        form = form_class(request.user)
        if not is_admin(request.user):
            del form.fields['activation_dt']
            del form.fields['entity']
        del form.fields['post_dt']
        del form.fields['expiration_dt']
          
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
    
@login_required
def edit(request, id, form_class=JobForm, template_name="jobs/edit.html"):
    job = get_object_or_404(Job, pk=id)

    if request.user.has_perm('jobs.change_job', job):    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=job)
            
            # delete admin only fields for non-admin on edit - GJQ 8/25/2010
            if not is_admin(request.user):
                del form.fields['requested_duration']
                del form.fields['list_type']
                del form.fields['activation_dt']
                del form.fields['post_dt']
                del form.fields['expiration_dt']
                del form.fields['entity']
            del form.fields['payment_method']
                
            if form.is_valid():
                job = form.save(commit=False)

                # remove all permissions on the object
                ObjectPermission.objects.remove_all(job)
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, job)               
                # assign creator permissions
                ObjectPermission.objects.assign(job.creator, job)

                job.save()

                log_defaults = {
                    'event_id' : 252000,
                    'event_data': '%s (%d) edited by %s' % (job._meta.object_name, job.pk, request.user),
                    'description': '%s edited' % job._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': job,
                }
                EventLog.objects.log(**log_defaults) 
                
                messages.add_message(request, messages.INFO, 'Successfully updated %s' % job)
                                                              
                return HttpResponseRedirect(reverse('job', args=[job.slug]))             
        else:
            form = form_class(request.user, instance=job)
            if not is_admin(request.user):
                del form.fields['requested_duration']
                del form.fields['list_type']
                del form.fields['activation_dt']
                del form.fields['post_dt']
                del form.fields['expiration_dt']
                del form.fields['entity']
            del form.fields['payment_method']

        return render_to_response(template_name, {'job': job, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="jobs/edit-meta.html"):

    # check permission
    job = get_object_or_404(Job, pk=id)
    if not request.user.has_perm('jobs.change_job', job):
        raise Http403

    defaults = {
        'title': job.get_title(),
        'description': job.get_description(),
        'keywords': job.get_keywords(),
    }
    job.meta = MetaTags(**defaults)


    if request.method == "POST":
        form = form_class(request.POST, instance=job.meta)
        if form.is_valid():
            job.meta = form.save() # save meta
            job.save() # save relationship

            messages.add_message(request, messages.INFO, 'Successfully updated meta for %s' % job)
            
            return HttpResponseRedirect(reverse('job', args=[job.slug]))
    else:
        form = form_class(instance=job.meta)

    return render_to_response(template_name, {'job': job, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="jobs/delete.html"):
    job = get_object_or_404(Job, pk=id)

    if request.user.has_perm('jobs.delete_job'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 433000,
                'event_data': '%s (%d) deleted by %s' % (job._meta.object_name, job.pk, request.user),
                'description': '%s deleted' % job._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job,
            }
            
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % job)
            
            # send notification to administrators
            recipients = get_notice_recipients('module', 'jobs', 'jobrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send_emails(recipients,'job_deleted', extra_context)
            
            job.delete()
                
            return HttpResponseRedirect(reverse('job.search'))
    
        return render_to_response(template_name, {'job': job}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def pricing_add(request, form_class=JobPricingForm, template_name="jobs/pricing-add.html"):
    if request.user.has_perm('jobs.add_jobpricing'):
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():           
                job_pricing = form.save(commit=False)
                job_pricing.status = 1
                job_pricing.save(request.user)
                
                log_defaults = {
                    'event_id' : 265100,
                    'event_data': '%s (%d) added by %s' % (job_pricing._meta.object_name, job_pricing.pk, request.user),
                    'description': '%s added' % job_pricing._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': job_pricing,
                }
                EventLog.objects.log(**log_defaults)
                
                return HttpResponseRedirect(reverse('job_pricing.view', args=[job_pricing.id]))
        else:
            form = form_class()
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def pricing_edit(request, id, form_class=JobPricingForm, template_name="jobs/pricing-edit.html"):
    job_pricing = get_object_or_404(JobPricing, pk=id)
    if not request.user.has_perm('jobs.change_jobpricing', job_pricing): Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=job_pricing)
        if form.is_valid():           
            job_pricing = form.save(commit=False)
            job_pricing.save(request.user)
            
            log_defaults = {
                'event_id' : 265110,
                'event_data': '%s (%d) edited by %s' % (job_pricing._meta.object_name, job_pricing.pk, request.user),
                'description': '%s edited' % job_pricing._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': job_pricing,
            }
            EventLog.objects.log(**log_defaults)
            
            return HttpResponseRedirect(reverse('job_pricing.view', args=[job_pricing.id]))
    else:
        form = form_class(instance=job_pricing)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))


@login_required
def pricing_view(request, id, template_name="jobs/pricing-view.html"):
    job_pricing = get_object_or_404(JobPricing, id=id)
    
    if request.user.has_perm('jobs.view_jobpricing', job_pricing):        
        return render_to_response(template_name, {'job_pricing': job_pricing}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def pricing_delete(request, id, template_name="jobs/pricing-delete.html"):
    job_pricing = get_object_or_404(JobPricing, pk=id)

    if not request.user.has_perm('jobs.delete_jobpricing'): raise Http403
       
    if request.method == "POST":
        log_defaults = {
            'event_id' : 265120,
            'event_data': '%s (%d) deleted by %s' % (job_pricing._meta.object_name, job_pricing.pk, request.user),
            'description': '%s deleted' % job_pricing._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': job_pricing,
        }
        
        EventLog.objects.log(**log_defaults)
        messages.add_message(request, messages.INFO, 'Successfully deleted %s' % job_pricing)
        
        job_pricing.delete()
            
        return HttpResponseRedirect(reverse('job_pricing.search'))
    
    return render_to_response(template_name, {'job_pricing': job_pricing}, 
        context_instance=RequestContext(request))

def pricing_search(request, template_name="jobs/pricing-search.html"):
    job_pricings = JobPricing.objects.all().order_by('duration')
    
    return render_to_response(template_name, {'job_pricings':job_pricings}, 
        context_instance=RequestContext(request))
    