from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.categories.forms import CategoryForm
from tendenci.apps.categories.models import Category
from tendenci.apps.files.models import File
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.committees.models import Committee, Officer
from tendenci.apps.committees.forms import CommitteeForm, OfficerForm, OfficerBaseFormSet
from tendenci.apps.perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters
from tendenci.apps.perms.fields import has_groups_perms

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


@is_enabled('committees')
def detail(request, slug, template_name="committees/detail.html"):
    committee = get_object_or_404(Committee, slug=slug)

    if has_perm(request.user, 'committees.view_committee', committee):
        EventLog.objects.log(instance=committee)
        officers = committee.officers()

        #has_group_view_permission is True if there is at least one
        #group where the user is a member that has a view_committee permission.
        has_group_view_permission = False
        #Check user for group view permissions
        if request.user.is_authenticated:
            groups = request.user.user_groups.all()
            perms = has_groups_perms(committee).filter(group__in=groups)
            for perm in perms:
                #Check if permission has view committee permission
                has_group_view_permission |= perm.codename == 'view_committee'
                if has_group_view_permission:
                    break

        filters = get_query_filters(request.user, 'files.view_file')
        files = File.objects.filter(filters).filter(group=committee.group).distinct()

        return render_to_resp(request=request, template_name=template_name,
            context={
                'committee': committee,
                'officers': officers,
                'files': files,
                'has_group_view_permission': has_group_view_permission,
            })
    else:
        raise Http403


@is_enabled('committees')
def search(request, template_name="committees/search.html"):
    query = request.GET.get('q', None)
    if query:
        committees = Committee.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'committees.view_committee')
        committees = Committee.objects.filter(filters).distinct()

    committees = committees.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'committees': committees})


@is_enabled('committees')
@login_required
def add(request, form_class=CommitteeForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="committees/add.html"):

    if not has_perm(request.user,'committees.add_committee'):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='committees',model='committee')

    #OfficerFormSet = inlineformset_factory(Committee, Officer, form=OfficerForm, extra=1)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, prefix='category')

        #formset = OfficerFormSet(request.POST, prefix="officers")

        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            committee = form.save(commit=False)
            committee = update_perms_and_save(request, form, committee)

            #save meta
            meta = metaform.save()
            committee.meta = meta

            #setup categories
            category = Category.objects.get_for_object(committee,'category')
            sub_category = Category.objects.get_for_object(committee,'sub_category')

            ## update the category of the committee
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(committee ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(committee ,'category')
                Category.objects.remove(committee ,'sub_category')

            if not category_removed:
                # update the sub category of the committee
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(committee, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(committee,'sub_category')

            #save relationships
            committee.save()

            EventLog.objects.log()

            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % committee)

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'committees', 'committeerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': committee,
                            'request': request,
                        }
                        notification.send_emails(recipients,'committee_added', extra_context)
            return HttpResponseRedirect(reverse('committees.detail', args=[committee.slug]))
    else:
        initial_category_form_data = {
            'app_label': 'committees',
            'model': 'committee',
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


@is_enabled('committees')
@login_required
def edit(request, id, form_class=CommitteeForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="committees/edit.html"):

    committee = get_object_or_404(Committee, pk=id)

    if not has_perm(request.user,'committees.change_committee',committee):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='committees',model='committee')

    #setup categories
    category = Category.objects.get_for_object(committee,'category')
    sub_category = Category.objects.get_for_object(committee,'sub_category')

    initial_category_form_data = {
        'app_label': 'committees',
        'model': 'committee',
        'pk': committee.pk,
        'category': getattr(category,'name','0'),
        'sub_category': getattr(sub_category,'name','0')
    }

    OfficerFormSet = inlineformset_factory(Committee, Officer, form=OfficerForm,
                                           formset=OfficerBaseFormSet, extra=1,)

    formset = OfficerFormSet(request.POST or None, instance=committee,
                             committee=committee, prefix="officers")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=committee, user=request.user)
        metaform = meta_form_class(request.POST, instance=committee.meta, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, initial= initial_category_form_data, prefix='category') 

        if form.is_valid() and metaform.is_valid() and categoryform.is_valid() and formset.is_valid():
            committee = form.save(commit=False)
            # update all permissions and save the model
            committee = update_perms_and_save(request, form, committee)

            #save meta
            meta = metaform.save()
            committee.meta = meta         

            ## update the category of the committee
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(committee ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(committee ,'category')
                Category.objects.remove(committee ,'sub_category')

            if not category_removed:
                # update the sub category of the committee
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(committee, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(committee,'sub_category')

            #save relationships
            committee.save()
            formset.save()

            EventLog.objects.log(instance=committee)

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % committee)

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'committees', 'committeerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': committee,
                            'request': request,
                        }
                        notification.send_emails(recipients, 'committee_edited', extra_context)

            return HttpResponseRedirect(reverse('committees.detail', args=[committee.slug]))
    else:
        form = form_class(instance=committee, user=request.user)
        metaform = meta_form_class(instance=committee.meta, prefix='meta')
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')
        #formset.form = staticmethod(curry(OfficerForm, committee_group=committee.group))

    return render_to_resp(request=request, template_name=template_name,
        context={
            'committee': committee,
            'form': form,
            'metaform': metaform,
            'categoryform': categoryform,
            'formset': formset,
        })


@is_enabled('committees')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="committees/edit-meta.html"):
    """
    Return committee that allows you to edit meta-html information.
    """

    # check permission
    committee = get_object_or_404(Committee, pk=id)
    if not has_perm(request.user, 'committees.change_committee', committee):
        raise Http403

    EventLog.objects.log(instance=committee)

    defaults = {
        'title': committee.get_title(),
        'description': committee.get_description(),
        'keywords': committee.get_keywords(),
        'canonical_url': committee.get_canonical_url(),
    }
    committee.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=committee.meta)
        if form.is_valid():
            committee.meta = form.save()  # save meta
            committee.save()  # save relationship

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % committee)

            return HttpResponseRedirect(reverse('committees.detail', args=[committee.slug]))
    else:
        form = form_class(instance=committee.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'committee': committee, 'form': form})


@is_enabled('committees')
@login_required
def delete(request, id, template_name="committees/delete.html"):
    committee = get_object_or_404(Committee, pk=id)

    if not has_perm(request.user, 'committees.delete_committee'):
        raise Http403

    if request.method == "POST":
        EventLog.objects.log(instance=committee)
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % committee)

        # send notification to administrators
        recipients = get_notice_recipients('module', 'committees', 'committeerecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': committee,
                    'request': request,
                }
                notification.send_emails(recipients, 'committee_deleted', extra_context)

        committee.delete()
        return HttpResponseRedirect(reverse('committees.search'))

    return render_to_resp(request=request, template_name=template_name,
        context={'committee': committee})
