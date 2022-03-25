
from builtins import str
import os
from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from tendenci.apps.base.http import Http403

from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (update_perms_and_save, get_notice_recipients,
    has_perm, has_view_perm, get_query_filters)
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task
from tendenci.apps.redirects.models import Redirect

from tendenci.apps.resumes.models import Resume
from tendenci.apps.resumes.forms import ResumeForm, ResumeExportForm, ResumeSearchForm

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


@is_enabled('resumes')
def index(request, slug=None, template_name="resumes/view.html"):
    if not get_setting('module', 'resumes', 'enabled'):
        redirect = get_object_or_404(Redirect, from_app='resumes')
        return HttpResponseRedirect('/' + redirect.to_url)

    if not slug: return HttpResponseRedirect(reverse('resume.search'))
    resume = get_object_or_404(Resume, slug=slug)

    if has_view_perm(request.user,'resumes.view_resume',resume):

        EventLog.objects.log()
        return render_to_resp(request=request, template_name=template_name,
            context={'resume': resume})
    else:
        raise Http403


def resume_file(request, slug=None, template_name="resumes/view.html"):
    if not slug: return HttpResponseRedirect(reverse('resume.search'))
    resume = get_object_or_404(Resume, slug=slug)

    if has_view_perm(request.user,'resumes.view_resume',resume):
        if resume.resume_file:

            EventLog.objects.log(instance=resume)
            response = HttpResponse(resume.resume_file)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (os.path.basename(str(resume.resume_file)))

            return response
        else:
            return HttpResponseRedirect(reverse('resume.search'))
    else:
        raise Http403


@is_enabled('resumes')
def search(request, template_name="resumes/search.html"):
    """
    This page lists out all resumes from newest to oldest.
    """
    filters = get_query_filters(request.user, 'resumes.view_resume')
    resumes = Resume.objects.filter(filters).distinct()
        
    form = ResumeSearchForm(request.GET, user=request.user)
    if form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        search_criteria = form.cleaned_data['search_criteria']
        search_text = form.cleaned_data['search_text']
        search_method = form.cleaned_data['search_method']
        grid_view = form.cleaned_data['grid_view']
        industry = form.cleaned_data.get('industry', None)
        if industry:
            industry = int(industry)
    else:
        first_name = None
        last_name = None
        email = None
        search_criteria = None
        search_text = None
        search_method = None
        grid_view = False
        industry = None
    
    if grid_view:
        num_items = 50
    else: 
        num_items = 10
                
    if first_name:
        resumes = resumes.filter(first_name__istartswith=first_name)
    if last_name:
        resumes = resumes.filter(last_name__istartswith=last_name)
    if email:
        resumes = resumes.filter(contact_email__istartswith=email)

    if search_criteria and search_text:
        search_type = '__iexact'
        if search_method == 'starts_with':
            search_type = '__istartswith'
        elif search_method == 'contains':
            search_type = '__icontains'

        search_filter = {'%s%s' % (search_criteria,
                                   search_type): search_text}
        resumes = resumes.filter(**search_filter)

    if industry:
        resumes = resumes.filter(industry_id=industry)

    resumes = resumes.order_by('-create_dt')

    EventLog.objects.log(**{
        'event_id' : 354000,
        'event_data': '%s searched by %s' % ('Resume', request.user),
        'description': '%s searched' % 'Resume',
        'user': request.user,
        'request': request,
        'source': 'resumes'
    })
    

    return render_to_resp(request=request, template_name=template_name,
        context={'resumes':resumes, 'form': form,
                 'is_grid_view': grid_view,
                 'num_items': num_items})

def search_redirect(request):
    """
    Redirects back to '/resumes/.' This catches links and
    bookmarks and sends them to the new list/search location.
    """
    return HttpResponseRedirect(reverse('resumes'))


@is_enabled('resumes')
def print_view(request, slug, template_name="resumes/print-view.html"):
    resume = get_object_or_404(Resume, slug=slug)

    EventLog.objects.log(instance=resume)

    if has_view_perm(request.user,'resumes.view_resume',resume):
        return render_to_resp(request=request, template_name=template_name,
            context={'resume': resume})
    else:
        raise Http403


@is_enabled('resumes')
@login_required
def add(request, form_class=ResumeForm, template_name="resumes/add.html"):
    can_add_active = has_perm(request.user, 'resumes.add_resume')
    
    if not any([request.user.profile.is_superuser,
               can_add_active,
               get_setting('module', 'resumes', 'usercanadd'),
               (request.user.profile.is_member and get_setting('module', 'resumes', 'userresumesrequiresmembership'))
               ]):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST or None, user=request.user)
        if form.is_valid():
            resume = form.save(commit=False)

            # set it to pending if the user does not have add permission
            if not can_add_active:
                resume.status_detail = 'pending'

            # set up the expiration time based on requested duration
            now = datetime.now()
            resume.expiration_dt = now + timedelta(days=resume.requested_duration)

            resume = update_perms_and_save(request, form, resume)
            # we need to save instance first since we need the id for the file path
            if request.FILES:
                resume.resume_file = request.FILES['resume_file']
                resume.resume_file.file.seek(0)
                resume.save()

            EventLog.objects.log(instance=resume)

            if request.user.is_authenticated:
                messages.add_message(request, messages.SUCCESS, _('Successfully added %(r)s' % {'r':resume}))

            # send notification to administrators
            recipients = get_notice_recipients('module', 'resumes', 'resumerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': resume,
                        'request': request,
                    }
                    notification.send_emails(recipients,'resume_added', extra_context)

            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('resume.thank_you'))
            else:
                return HttpResponseRedirect(reverse('resume', args=[resume.slug]))
    else:
        form = form_class(user=request.user)
    return render_to_resp(request=request, template_name=template_name,
        context={'form':form})


@is_enabled('resumes')
@login_required
def edit(request, id, form_class=ResumeForm, template_name="resumes/edit.html"):
    resume = get_object_or_404(Resume, pk=id)

    form = form_class(request.POST or None, request.FILES or None, instance=resume, user=request.user)
    if has_perm(request.user,'resumes.change_resume',resume):
        if request.method == "POST":
            if form.is_valid():
                resume = form.save(commit=False)

                if resume.resume_file:
                    resume.resume_file.file.seek(0)
                resume = update_perms_and_save(request, form, resume)

                EventLog.objects.log(instance=resume)

                messages.add_message(request, messages.SUCCESS, _('Successfully updated %(r)s' % {'r':resume}))

                return HttpResponseRedirect(reverse('resume', args=[resume.slug]))

        return render_to_resp(request=request, template_name=template_name,
            context={'resume': resume, 'form':form})
    else:
        raise Http403


@is_enabled('resumes')
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

            messages.add_message(request, messages.SUCCESS, _('Successfully updated meta for %(r)s' % { 'r':resume}))

            return HttpResponseRedirect(reverse('resume', args=[resume.slug]))
    else:
        form = form_class(instance=resume.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'resume': resume, 'form':form})


@is_enabled('resumes')
@login_required
def delete(request, id, template_name="resumes/delete.html"):
    resume = get_object_or_404(Resume, pk=id)

    if has_perm(request.user,'resumes.delete_resume'):
        if request.method == "POST":

            EventLog.objects.log(instance=resume)
            messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(r)s' % {'r':resume}))

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

        return render_to_resp(request=request, template_name=template_name,
            context={'resume': resume})
    else:
        raise Http403


@is_enabled('resumes')
@login_required
def pending(request, template_name="resumes/pending.html"):
    if not request.user.profile.is_superuser:
        raise Http403
    resumes = Resume.objects.filter(status_detail='pending')
    return render_to_resp(request=request, template_name=template_name,
            context={'resumes': resumes})


@login_required
def approve(request, id, template_name="resumes/approve.html"):
    if not request.user.profile.is_superuser:
        raise Http403
    resume = get_object_or_404(Resume, pk=id)

    if request.method == "POST":
        resume.activation_dt = datetime.now()
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

        messages.add_message(request, messages.SUCCESS, _('Successfully approved %(r)s' % {'r':resume}))

        return HttpResponseRedirect(reverse('resume', args=[resume.slug]))

    return render_to_resp(request=request, template_name=template_name,
            context={'resume': resume})

def thank_you(request, template_name="resumes/thank-you.html"):
    return render_to_resp(request=request, template_name=template_name)


@is_enabled('resumes')
@login_required
def export(request, template_name="resumes/export.html"):
    """Export Resumes"""
    if not request.user.is_superuser:
        raise Http403

    form = ResumeExportForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        start_dt = form.cleaned_data['start_dt']
        end_dt = form.cleaned_data['end_dt']
        include_files = form.cleaned_data['include_files']
        if start_dt and end_dt:
            start_dt = start_dt.strftime('%m/%d/%Y')
            end_dt = end_dt.strftime('%m/%d/%Y')
            kwargs = {'start_dt': start_dt, 'end_dt': end_dt}
        else:
            kwargs = {}
        if include_files:
            kwargs.update({'include_files': 'True'})
        # initilize initial values
        fields = [
            'guid',
            'title',
            'slug',
            'description',
            'location',
            'skills',
            'experience',
            'education',
            'is_agency',
            'list_type',
            'requested_duration',
            'activation_dt',
            'expiration_dt',
            'resume_url',
            'syndicate',
            'first_name',
            'last_name',
            'contact_address',
            'contact_address2',
            'contact_city',
            'contact_state',
            'contact_zip_code',
            'contact_country',
            'contact_phone',
            'contact_phone2',
            'contact_fax',
            'contact_email',
            'contact_website',
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_user_edit',
            'allow_member_edit',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail',
            'meta',
            'tags',
        ]
        
        export_id = run_export_task('resumes', 'resume', fields, **kwargs)
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name,
                          context={'form': form})
