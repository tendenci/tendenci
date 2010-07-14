from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from jobs.models import Job
from jobs.forms import JobForm
from perms.models import ObjectPermission
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm

from perms.utils import get_administrators

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
    jobs = Job.objects.search(query)

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
        'event_id' : 255000,
        'event_data': '%s (%d) viewed by %s' % (job._meta.object_name, job.pk, request.user),
        'description': '%s viewed' % job._meta.object_name,
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
    if request.user.has_perm('jobs.add_job'):
        if request.method == "POST":
            form = form_class(request.user, request.POST)
            if form.is_valid():           
                job = form.save(commit=False)
                # set up the user information
                job.creator = request.user
                job.creator_username = request.user.username
                job.owner = request.user
                job.owner_username = request.user.username
                job.save()

                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, job)
                # assign creator permissions
                ObjectPermission.objects.assign(job.creator, job) 

                job.save() # update search-index w/ permissions
 
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
                if notification:
                    extra_context = {
                        'object': job,
                        'request': request,
                    }
                    notification.send(get_administrators(),'job_added', extra_context)
                
                return HttpResponseRedirect(reverse('job', args=[job.slug]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=JobForm, template_name="jobs/edit.html"):
    job = get_object_or_404(Job, pk=id)

    if request.user.has_perm('jobs.change_job', job):    
        if request.method == "POST":
            form = form_class(request.user, request.POST, instance=job)
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
            if notification:
                extra_context = {
                    'object': job,
                    'request': request,
                }
                notification.send(get_administrators(),'job_deleted', extra_context)
            
            job.delete()
                
            return HttpResponseRedirect(reverse('job.search'))
    
        return render_to_response(template_name, {'job': job}, 
            context_instance=RequestContext(request))
    else:
        raise Http403