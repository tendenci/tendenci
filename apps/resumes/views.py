from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.http import Http403
from base.utils import now_localized
from site_settings.utils import get_setting
from resumes.models import Resume
from resumes.forms import ResumeForm
from perms.object_perms import ObjectPermission
from perms.utils import update_perms_and_save, get_notice_recipients, is_admin, has_perm, has_view_perm, get_query_filters
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from notification import models as notification

def index(request, slug=None, template_name="resumes/view.html"):
    if not slug: return HttpResponseRedirect(reverse('resume.search'))
    resume = get_object_or_404(Resume, slug=slug)
    
    if has_view_perm(request.user,'resumes.view_resume',resume):
        log_defaults = {
            'event_id' : 355000,
            'event_data': '%s (%d) viewed by %s' % (resume._meta.object_name, resume.pk, request.user),
            'description': '%s viewed' % resume._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': resume,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'resume': resume}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="resumes/list.html"):
    """
    This page lists out all resumes from newest to oldest.
    If a search index is available, this page will also
    have the option to search through resumes.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        resumes = Resume.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'resumes.view_resume')
        resumes = Resume.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            resumes = resumes.select_related()
        resumes = resumes.order_by('-create_dt')

    EventLog.objects.log(**{
        'event_id' : 354000,
        'event_data': '%s searched by %s' % ('Resume', request.user),
        'description': '%s searched' % 'Resume',
        'user': request.user,
        'request': request,
        'source': 'resumes'
    })
    
    return render_to_response(template_name, {'resumes':resumes}, 
        context_instance=RequestContext(request))

def search_redirect(request):
    """
    Redirects back to '/resumes/.' This catches links and
    bookmarks and sends them to the new list/search location.
    """
    return HttpResponseRedirect(reverse('resumes'))

def print_view(request, slug, template_name="resumes/print-view.html"):
    resume = get_object_or_404(Resume, slug=slug)    

    log_defaults = {
        'event_id' : 355001,
        'event_data': '%s (%d) viewed by %s' % (resume._meta.object_name, resume.pk, request.user),
        'description': '%s viewed - print view' % resume._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': resume,
    }
    EventLog.objects.log(**log_defaults)
       
    if has_view_perm(request.user,'resumes.view_resume',resume):
        return render_to_response(template_name, {'resume': resume}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=ResumeForm, template_name="resumes/add.html"):

    can_add_active = has_perm(request.user, 'resumes.add_resume')

    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            resume = form.save(commit=False)

            # set it to pending if the user does not have add permission
            if not can_add_active:
                resume.status = 0
                resume.status_detail = 'pending'

            # set up the expiration time based on requested duration
            now = now_localized()
            resume.expiration_dt = now + timedelta(days=resume.requested_duration)

            resume = update_perms_and_save(request, form, resume)

            log_defaults = {
                'event_id' : 351000,
                'event_data': '%s (%d) added by %s' % (resume._meta.object_name, resume.pk, request.user),
                'description': '%s added' % resume._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': resume,
            }
            EventLog.objects.log(**log_defaults)

            if request.user.is_authenticated():
                messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % resume)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'resumes', 'resumerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': resume,
                        'request': request,
                    }
                    notification.send_emails(recipients,'resume_added', extra_context)

            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('resume.thank_you'))
            else:
                return HttpResponseRedirect(reverse('resume', args=[resume.slug]))
    else:
        form = form_class(user=request.user)

    return render_to_response(template_name, {'form':form},
        context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=ResumeForm, template_name="resumes/edit.html"):
    resume = get_object_or_404(Resume, pk=id)

    if has_perm(request.user,'resumes.change_resume',resume):    
        if request.method == "POST":
            form = form_class(request.POST, instance=resume, user=request.user)
            if form.is_valid():
                resume = form.save(commit=False)
                resume = update_perms_and_save(request, form, resume)

                log_defaults = {
                    'event_id' : 352000,
                    'event_data': '%s (%d) edited by %s' % (resume._meta.object_name, resume.pk, request.user),
                    'description': '%s edited' % resume._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': resume,
                }
                EventLog.objects.log(**log_defaults) 
                
                messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % resume)
                                                              
                return HttpResponseRedirect(reverse('resume', args=[resume.slug]))             
        else:
            form = form_class(instance=resume, user=request.user)

        return render_to_response(template_name, {'resume': resume, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="resumes/edit-meta.html"):

    # check permission
    resume = get_object_or_404(Resume, pk=id)
    if not has_perm(request.user,'resumes.change_resume',resume):
        raise Http403

    defaults = {
        'title': resume.get_title(),
        'description': resume.get_description(),
        'keywords': resume.get_keywords(),
        'canonical_url': resume.get_canonical_url(),
    }
    resume.meta = MetaTags(**defaults)


    if request.method == "POST":
        form = form_class(request.POST, instance=resume.meta)
        if form.is_valid():
            resume.meta = form.save() # save meta
            resume.save() # save relationship

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % resume)
            
            return HttpResponseRedirect(reverse('resume', args=[resume.slug]))
    else:
        form = form_class(instance=resume.meta)

    return render_to_response(template_name, {'resume': resume, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="resumes/delete.html"):
    resume = get_object_or_404(Resume, pk=id)

    if has_perm(request.user,'resumes.delete_resume'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 433000,
                'event_data': '%s (%d) deleted by %s' % (resume._meta.object_name, resume.pk, request.user),
                'description': '%s deleted' % resume._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': resume,
            }
            
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % resume)
            
            # send notification to administrators
            recipients = get_notice_recipients('module', 'resumes', 'resumerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': resume,
                        'request': request,
                    }
                    notification.send_emails(recipients,'resume_deleted', extra_context)
            
            resume.delete()
                
            return HttpResponseRedirect(reverse('resume.search'))
    
        return render_to_response(template_name, {'resume': resume}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def pending(request, template_name="resumes/pending.html"):
    if not is_admin(request.user):
        raise Http403
    resumes = Resume.objects.filter(status=0, status_detail='pending')
    return render_to_response(template_name, {'resumes': resumes},
            context_instance=RequestContext(request))

@login_required
def approve(request, id, template_name="resumes/approve.html"):
    if not is_admin(request.user):
        raise Http403
    resume = get_object_or_404(Resume, pk=id)

    if request.method == "POST":
        resume.activation_dt = now_localized()
        resume.allow_anonymous_view = True
        resume.status = True
        resume.status_detail = 'active'

        if not resume.creator:
            resume.creator = request.user
            resume.creator_username = request.user.username

        if not resume.owner:
            resume.owner = request.user
            resume.owner_username = request.user.username

        resume.save()

        messages.add_message(request, messages.SUCCESS, 'Successfully approved %s' % resume)

        return HttpResponseRedirect(reverse('resume', args=[resume.slug]))

    return render_to_response(template_name, {'resume': resume},
            context_instance=RequestContext(request))

def thank_you(request, template_name="resumes/thank-you.html"):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))