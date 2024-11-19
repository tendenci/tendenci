from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.generic import CreateView, UpdateView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.projects.models import Project, Category
from tendenci.apps.projects.forms import (ProjectFrontForm, PhotoFormSet,
                                          DocumentsFormSet, TeamMembersFormSet,
                                          ProjectSearchForm)
from tendenci.apps.perms.utils import has_perm, get_query_filters
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.notifications import models as notification
from tendenci.apps.base.utils import validate_email
from tendenci.apps.perms.utils import update_perms_and_save


class ProjectInline():
    form_class = ProjectFrontForm
    model = Project
    template_name = "projects/project_create_or_update.html"

    def get_form_kwargs(self):
        """
        Pass request user to the form.
        """
        kwargs = super(ProjectInline, self).get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        ctx = self.get_context_data(form=form)
        edit_mode = ctx.get('edit_mode', False)
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(ctx)

        self.object = form.save(commit=False)
        # set to pending for non-admins
        if not edit_mode and not self.request.user.is_superuser:
            self.object.status_detail = 'pending'
            self.object.allow_anonymous_view = False

        self.object = update_perms_and_save(self.request, form, self.object, log=False)
        form.save_m2m()

        # for each formset, use custom formset save func if available
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        if edit_mode:
            msg_string = f'Successfully updated {self.object.project_name}.'
        else:
            msg_string = f'Successfully added {self.object.project_name}.'
            if self.object.status_detail == 'pending':
                project_label = get_setting("module", "projects", "label")
                msg_string += f' You will be notified when this {project_label} is approved.'
        messages.add_message(self.request, messages.SUCCESS, _(msg_string))

        # notify admin
        if not edit_mode and not self.request.user.is_superuser:
            # send notification to admins and module recipient(s)
            recipients = get_notice_recipients('module', 'projects', 'projectrecipients')
            if recipients and notification:
                notification.send_emails(recipients, 'project_added', {
                    'object': self.object,
                    'request': self.request,
                    'MODULE_PROJECTS_LABEL':
                         get_setting('module', 'projects', 'label')
                })

        # log an event
        log_defaults = {
            'instance': self.object,
        }
        if not edit_mode:
            log_defaults['action'] = "add"
        else:
            log_defaults['action'] = "edit"
        EventLog.objects.log(**log_defaults)

        return HttpResponseRedirect(self.get_success_url())

    def formset_photos_valid(self, formset):
        """
        custom formset save function for photos
        """
        if not formset.is_valid():
            print('formset=', formset)
        content_type = ContentType.objects.get_for_model(self.object)

        photos = formset.save(commit=False)
        
        for obj in formset.deleted_objects:
            obj.delete()

        for photo in photos:
            photo.project = self.object
            photo.save()
            if photo.file:
                if not photo.content_type:
                    photo.content_type = content_type
                    photo.object_id = self.object.id
                if not photo.creator:
                    photo.creator = self.request.user
                    photo.creator_username = self.request.user.username
                photo.owner = self.request.user
                photo.owner_username = self.request.user.username
                photo.save()

    def formset_documents_valid(self, formset):
        """
        custom formset save function for documents
        """
        content_type = ContentType.objects.get_for_model(self.object)

        documents = formset.save(commit=False)
        
        for obj in formset.deleted_objects:
            obj.delete()

        for document in documents:
            document.project = self.object
            document.save()
            if document.file:
                if not document.content_type:
                    document.content_type = content_type
                    document.object_id = self.object.id
                if not document.creator:
                    document.creator = self.request.user
                    document.creator_username = self.request.user.username
                document.owner = self.request.user
                document.owner_username = self.request.user.username
                document.save()

    def formset_teammembers_valid(self, formset):
        """
        custom formset save function for teammembers
        """
        content_type = ContentType.objects.get_for_model(self.object)

        teammembers = formset.save(commit=False)
        
        for obj in formset.deleted_objects:
            obj.delete()

        for teammember in teammembers:
            teammember.project = self.object
            teammember.save()
            if teammember.file:
                if not teammember.content_type:
                    teammember.content_type = content_type
                    teammember.object_id = self.object.id
                if not teammember.creator:
                    teammember.creator = self.request.user
                    teammember.creator_username = self.request.user.username
                teammember.owner = self.request.user
                teammember.owner_username = self.request.user.username
                teammember.save()


class ProjectCreate(ProjectInline, CreateView):

    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if not has_perm(request.user, 'projects.add_project'):
            return HttpResponseForbidden()
        return super(ProjectCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ProjectCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['edit_mode'] = False
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'photos': PhotoFormSet(prefix='photos'),
                'documents': DocumentsFormSet(prefix='documents'),
                'teammembers': TeamMembersFormSet(prefix='teammembers')
            }
        else:
            return {
                'photos': PhotoFormSet(self.request.POST or None, self.request.FILES or None, prefix='photos'),
                'documents': DocumentsFormSet(self.request.POST or None, self.request.FILES or None, prefix='documents'),
                'teammembers': TeamMembersFormSet(self.request.POST or None, self.request.FILES or None, prefix='teammembers'),
            }


class ProjectUpdate(ProjectInline, UpdateView):

    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        if not has_perm(request.user, 'projects.change_project', project):
            return HttpResponseForbidden()
        return super(ProjectUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ProjectUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['edit_mode'] = True
        return ctx

    def get_named_formsets(self):
        return {
            'photos': PhotoFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='photos'),
            'documents': DocumentsFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='documents'),
            'teammembers': TeamMembersFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='teammembers'),
        }


@login_required
def approve(request, id, template_name="projects/approve.html"):
    # only superuser can approve
    if not request.user.is_superuser:
        raise Http403

    project = get_object_or_404(Project, pk=id)

    if request.method == "POST":
        project.status_detail = 'active'

        if not project.owner:
            project.owner = request.user
            project.owner_username = request.user.username

        project.save()

        # send email notification to user
        if project.creator and validate_email(project.creator.email):
            notification.send_emails([project.creator.email], 
                'project_approved_user_notice', {
                        'object': project,
                        'request': request,
                        'MODULE_PROJECTS_LABEL':
                         get_setting('module', 'projects', 'label')})

        msg_string = f'Successfully approved {project.project_name}'
        messages.add_message(request, messages.SUCCESS, _(msg_string))

        return HttpResponseRedirect(project.get_absolute_url())

    return render_to_resp(request=request, template_name=template_name,
            context={'project': project})


def index(request, template_name="projects/detail.html"):
    return HttpResponseRedirect(reverse('projects.search'))


def detail(request, slug=None, template_name="projects/detail.html"):
    if not slug:
        return HttpResponseRedirect(reverse('projects.search'))

    project = get_object_or_404(Project, slug=slug)
    if not has_perm(request.user, 'projects.view_project', project):
        raise Http403

    project_photos = project.projects_photo_related.all()
    team_members = project.projects_teammembers_related.all()
    documents = project.projects_documents_related.all().order_by('-document_dt')
    
    log_defaults = {
        'event_id': 1180500,
        'event_data': '%s (%d) viewed by %s' % (project._meta.object_name, project.pk, request.user),
        'description': '%s viewed' % project._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': project,
    }
    EventLog.objects.log(**log_defaults)

    return render_to_resp(request=request, template_name=template_name,
        context={'project': project,
                 'project_photos': project_photos,
                 'team_members': team_members,
                 'documents': documents,
                 'can_edit': has_perm(request.user, 'projects.change_project', project)})


def search(request, template_name="projects/search.html"):
    if request.user.is_authenticated and has_perm(request.user, 'projects.view_project'):
        projects = Project.objects.filter(status=True,
                                           status_detail__in=['active', 'published'])
    else:
        filters = get_query_filters(request.user, 'projects.view_project')
        projects = Project.objects.filter(filters).distinct()

    form = ProjectSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('q')
        if query:
            if 'tag:' in query:
                tag = query.strip('tag:')
                projects = projects.filter(tags__icontains=tag)
            else:
                projects = projects.filter(Q(project_name__icontains=query) | Q(company_name__icontains=query))

        category = form.cleaned_data.get('category')
        if category:
            projects = projects.filter(category=category)

    if get_setting('module', 'projects', 'availableonly'):
        now = datetime.now()
        projects = projects.filter(start_dt__lte=now).filter(Q(end_dt__isnull=True) | Q(end_dt__gt=now))
        projects = projects.filter(status_detail='active')
        projects = projects.order_by('-start_dt')

    log_defaults = {
        'event_id' : 1180400,
        'event_data': '%s searched by %s' % ('Project', request.user),
        'description': '%s searched' % 'Project',
        'user': request.user,
        'request': request,
        'source': 'projects'
    }
    EventLog.objects.log(**log_defaults)

    return render_to_resp(request=request, template_name=template_name,
        context={'projects':projects,
                 'categories': Category.objects.all(), # needed for some custom projects
                 'form': form,
                 'can_add_project': has_perm(request.user, 'projects.add_project')
        })

def category(request, template_name="projects/category.html"):
    query = request.GET.get('q', None)

    if get_setting('site', 'global', 'searchindex') and query:
        projects = Project.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'projects.search')
        projects = Project.objects.filter(filters).distinct()

    categories = Category.objects.all()
    category_id = request.GET.get('category', None)

    if category_id:
        try:
            category = Category.objects.get(pk=category_id)
        except:
            category = None

        if category:
            projects = projects.filter(category=category)

    log_defaults = {
        'event_id' : 1180400,
        'event_data': '%s searched by %s' % ('Project', request.user),
        'description': '%s searched' % 'Project',
        'user': request.user,
        'request': request,
        'source': 'projects'
    }

    EventLog.objects.log(**log_defaults)

    return render_to_resp(request=request, template_name=template_name,
        context={'projects':projects, 'categories': categories
        })
