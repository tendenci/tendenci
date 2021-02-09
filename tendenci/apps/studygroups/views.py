from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms.models import inlineformset_factory
from django.contrib import messages
#from django.utils.functional import curry
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.categories.forms import CategoryForm
from tendenci.apps.categories.models import Category
from tendenci.apps.files.models import File
from tendenci.apps.studygroups.models import StudyGroup, Officer
from tendenci.apps.studygroups.forms import StudyGroupForm, OfficerForm, OfficerBaseFormSet
from tendenci.apps.perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters
from tendenci.apps.perms.fields import has_groups_perms
from tendenci.apps.perms.decorators import is_enabled

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


@is_enabled('studygroups')
def detail(request, slug, template_name="studygroups/detail.html"):
    study_group = get_object_or_404(StudyGroup, slug=slug)

    if has_perm(request.user, 'studygroups.view_studygroup', study_group):
        EventLog.objects.log(instance=study_group)
        officers = study_group.officers()

        #has_group_view_permission is True if there is at least one
        #group where the user is a member that has a view_studygroup permission.
        has_group_view_permission = False
        #Check user for group view permissions
        if request.user.is_authenticated:
            groups = request.user.user_groups.all()
            perms = has_groups_perms(study_group).filter(group__in=groups)
            for perm in perms:
                #Check if permission has view studygroup permission
                has_group_view_permission |= perm.codename == 'view_studygroup'
                if has_group_view_permission:
                    break

        filters = get_query_filters(request.user, 'files.view_file')
        files = File.objects.filter(filters).filter(group=study_group.group).distinct()

        return render_to_resp(request=request, template_name=template_name,
            context={
                'study_group': study_group,
                'officers': officers,
                'files': files,
                'has_group_view_permission': has_group_view_permission,
            })
    else:
        raise Http403


@is_enabled('studygroups')
def search(request, template_name="studygroups/search.html"):
    query = request.GET.get('q', None)
    if query:
        studygroups = StudyGroup.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'studygroups.view_studygroup')
        studygroups = StudyGroup.objects.filter(filters).distinct()

    studygroups = studygroups.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'studygroups': studygroups})


@is_enabled('studygroups')
@login_required
def add(request, form_class=StudyGroupForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="studygroups/add.html"):

    if not has_perm(request.user,'studygroups.add_studygroup'):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='studygroups',model='studygroup')

    #OfficerFormSet = inlineformset_factory(StudyGroup, Officer, form=OfficerForm, extra=1)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, prefix='category')

        #formset = OfficerFormSet(request.POST, prefix="officers")

        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            study_group = form.save(commit=False)
            study_group = update_perms_and_save(request, form, study_group)

            #save meta
            meta = metaform.save()
            study_group.meta = meta

            #setup categories
            category = Category.objects.get_for_object(study_group,'category')
            sub_category = Category.objects.get_for_object(study_group,'sub_category')

            ## update the category of the studygroup
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(study_group ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(study_group ,'category')
                Category.objects.remove(study_group ,'sub_category')

            if not category_removed:
                # update the sub category of the studygroup
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(study_group, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(study_group,'sub_category')

            #save relationships
            study_group.save()

            EventLog.objects.log()

            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % study_group)

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'studygroups', 'studygrouprecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': study_group,
                            'request': request,
                        }
                        notification.send_emails(recipients,'study_group_added', extra_context)
            return HttpResponseRedirect(reverse('studygroups.detail', args=[study_group.slug]))
    else:
        initial_category_form_data = {
            'app_label': 'studygroups',
            'model': 'studygroup',
            'pk': 0, #not used for this view but is required for the form
        }
        form = form_class(user=request.user)
        metaform = meta_form_class(prefix='meta')
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')

    return render_to_resp(request=request, template_name=template_name,
            context={
                'form':form,
                'metaform':metaform,
                'categoryform':categoryform,
            })


@is_enabled('studygroups')
@login_required
def edit(request, id, form_class=StudyGroupForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="studygroups/edit.html"):

    study_group = get_object_or_404(StudyGroup, pk=id)

    if not has_perm(request.user,'studygroups.change_studygroup',study_group):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='studygroups',model='studygroup')

    #setup categories
    category = Category.objects.get_for_object(study_group,'category')
    sub_category = Category.objects.get_for_object(study_group,'sub_category')

    initial_category_form_data = {
        'app_label': 'studygroups',
        'model': 'studygroup',
        'pk': study_group.pk,
        'category': getattr(category,'name','0'),
        'sub_category': getattr(sub_category,'name','0')
    }

    OfficerFormSet = inlineformset_factory(StudyGroup, Officer, form=OfficerForm,
                                           formset=OfficerBaseFormSet, extra=1,)
    formset = OfficerFormSet(request.POST or None, instance=study_group,
                             study_group=study_group, prefix="officers")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=study_group, user=request.user)
        metaform = meta_form_class(request.POST, instance=study_group.meta, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, initial= initial_category_form_data, prefix='category')

        if form.is_valid() and metaform.is_valid() and categoryform.is_valid() and formset.is_valid():
            study_group = form.save(commit=False)
            # update all permissions and save the model
            study_group = update_perms_and_save(request, form, study_group)

            #save meta
            meta = metaform.save()
            study_group.meta = meta

            ## update the category of the studygroup
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(study_group ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(study_group ,'category')
                Category.objects.remove(study_group ,'sub_category')

            if not category_removed:
                # update the sub category of the studygroup
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(study_group, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(study_group,'sub_category')

            #save relationships
            study_group.save()
            formset.save()

            EventLog.objects.log(instance=study_group)

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % study_group)

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'studygroups', 'studygrouprecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': study_group,
                            'request': request,
                        }
                        notification.send_emails(recipients, 'study_group_edited', extra_context)

            return HttpResponseRedirect(reverse('studygroups.detail', args=[study_group.slug]))
    else:
        form = form_class(instance=study_group, user=request.user)
        metaform = meta_form_class(instance=study_group.meta, prefix='meta')
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')
        #formset.form = staticmethod(curry(OfficerForm, study_group_group=study_group.group))

    return render_to_resp(request=request, template_name=template_name,
        context={
            'study_group': study_group,
            'form': form,
            'metaform': metaform,
            'categoryform': categoryform,
            'formset': formset,
        })


@is_enabled('studygroups')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="studygroups/edit-meta.html"):
    """
    Return study group that allows you to edit meta-html information.
    """

    # check permission
    study_group = get_object_or_404(StudyGroup, pk=id)
    if not has_perm(request.user, 'studygroups.change_studygroup', study_group):
        raise Http403

    EventLog.objects.log(instance=study_group)

    defaults = {
        'title': study_group.get_title(),
        'description': study_group.get_description(),
        'keywords': study_group.get_keywords(),
        'canonical_url': study_group.get_canonical_url(),
    }
    study_group.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=study_group.meta)
        if form.is_valid():
            study_group.meta = form.save()  # save meta
            study_group.save()  # save relationship

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % study_group)

            return HttpResponseRedirect(reverse('studygroups.detail', args=[study_group.slug]))
    else:
        form = form_class(instance=study_group.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'study_group': study_group, 'form': form})


@is_enabled('studygroups')
@login_required
def delete(request, id, template_name="studygroups/delete.html"):
    study_group = get_object_or_404(StudyGroup, pk=id)

    if not has_perm(request.user, 'studygroups.delete_studygroup'):
        raise Http403

    if request.method == "POST":
        EventLog.objects.log(instance=study_group)
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % study_group)

        # send notification to administrators
        recipients = get_notice_recipients('module', 'studygroups', 'studygrouprecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': study_group,
                    'request': request,
                }
                notification.send_emails(recipients, 'studygroup_deleted', extra_context)

        study_group.delete()
        return HttpResponseRedirect(reverse('studygroups.search'))

    return render_to_resp(request=request, template_name=template_name,
        context={'study_group': study_group})
