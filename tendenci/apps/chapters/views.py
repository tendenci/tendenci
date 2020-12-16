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
from tendenci.apps.chapters.models import Chapter, Officer
from tendenci.apps.chapters.forms import ChapterForm, OfficerForm, OfficerBaseFormSet
from tendenci.apps.perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters
from tendenci.apps.perms.fields import has_groups_perms

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


@is_enabled('chapters')
def detail(request, slug, template_name="chapters/detail.html"):
    chapter = get_object_or_404(Chapter, slug=slug)

    if has_perm(request.user, 'chapters.view_chapter', chapter):
        EventLog.objects.log(instance=chapter)
        officers = chapter.officers()

        #has_group_view_permission is True if there is at least one
        #group where the user is a member that has a view_chapter permission.
        has_group_view_permission = False
        #Check user for group view permissions
        if request.user.is_authenticated:
            groups = request.user.user_groups.all()
            perms = has_groups_perms(chapter).filter(group__in=groups)
            for perm in perms:
                #Check if permission has view chapter permission
                has_group_view_permission |= perm.codename == 'view_chapter'
                if has_group_view_permission:
                    break

        filters = get_query_filters(request.user, 'files.view_file')
        files = File.objects.filter(filters).filter(group=chapter.group).distinct()

        return render_to_resp(request=request, template_name=template_name,
            context={
                'chapter': chapter,
                'officers': officers,
                'files': files,
                'has_group_view_permission': has_group_view_permission,
            })
    else:
        raise Http403


@is_enabled('chapters')
def search(request, template_name="chapters/search.html"):
    query = request.GET.get('q', None)
    if query:
        chapters = Chapter.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'chapters.view_chapter')
        chapters = Chapter.objects.filter(filters).distinct()

    chapters = chapters.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'chapters': chapters})


@is_enabled('chapters')
@login_required
def add(request, form_class=ChapterForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="chapters/add.html"):

    if not has_perm(request.user,'chapters.add_chapter'):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='chapters',model='chapter')

    #OfficerFormSet = inlineformset_factory(Chapter, Officer, form=OfficerForm, extra=1)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, prefix='category')

        #formset = OfficerFormSet(request.POST, prefix="officers")

        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            chapter = form.save(commit=False)
            chapter = update_perms_and_save(request, form, chapter)

            #save meta
            meta = metaform.save()
            chapter.meta = meta

            #setup categories
            category = Category.objects.get_for_object(chapter,'category')
            sub_category = Category.objects.get_for_object(chapter,'sub_category')

            ## update the category of the chapter
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(chapter ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(chapter ,'category')
                Category.objects.remove(chapter ,'sub_category')

            if not category_removed:
                # update the sub category of the chapter
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(chapter, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(chapter,'sub_category')

            #save relationships
            chapter.save()

            EventLog.objects.log()

            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % chapter)

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'chapters', 'chapterrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': chapter,
                            'request': request,
                        }
                        notification.send_emails(recipients,'chapter_added', extra_context)
            return HttpResponseRedirect(reverse('chapters.detail', args=[chapter.slug]))
    else:
        initial_category_form_data = {
            'app_label': 'chapters',
            'model': 'chapter',
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


@is_enabled('chapters')
@login_required
def edit(request, id, form_class=ChapterForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="chapters/edit.html"):

    chapter = get_object_or_404(Chapter, pk=id)

    if not has_perm(request.user,'chapters.change_chapter',chapter):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='chapters',model='chapter')

    #setup categories
    category = Category.objects.get_for_object(chapter,'category')
    sub_category = Category.objects.get_for_object(chapter,'sub_category')

    initial_category_form_data = {
        'app_label': 'chapters',
        'model': 'chapter',
        'pk': chapter.pk,
        'category': getattr(category,'name','0'),
        'sub_category': getattr(sub_category,'name','0')
    }

    OfficerFormSet = inlineformset_factory(Chapter, Officer, form=OfficerForm,
                                           formset=OfficerBaseFormSet, extra=1,)

    formset = OfficerFormSet(request.POST or None, instance=chapter,
                             chapter=chapter, prefix="officers")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=chapter, user=request.user)
        metaform = meta_form_class(request.POST, instance=chapter.meta, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, initial= initial_category_form_data, prefix='category') 

        if form.is_valid() and metaform.is_valid() and categoryform.is_valid() and formset.is_valid():
            chapter = form.save()

            # update all permissions and save the model
            chapter = update_perms_and_save(request, form, chapter)

            #save meta
            meta = metaform.save()
            chapter.meta = meta         

            ## update the category of the chapter
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0':
                Category.objects.update(chapter ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(chapter ,'category')
                Category.objects.remove(chapter ,'sub_category')

            if not category_removed:
                # update the sub category of the chapter
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(chapter, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(chapter,'sub_category')

            #save relationships
            chapter.save()
            formset.save()

            EventLog.objects.log(instance=chapter)

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % chapter)

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'chapters', 'chapterrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': chapter,
                            'request': request,
                        }
                        notification.send_emails(recipients, 'chapter_edited', extra_context)

            return HttpResponseRedirect(reverse('chapters.detail', args=[chapter.slug]))
    else:
        form = form_class(instance=chapter, user=request.user)
        metaform = meta_form_class(instance=chapter.meta, prefix='meta')
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')
        #formset.form = staticmethod(curry(OfficerForm, chapter_group=chapter.group))

    return render_to_resp(request=request, template_name=template_name,
        context={
            'chapter': chapter,
            'form': form,
            'metaform': metaform,
            'categoryform': categoryform,
            'formset': formset,
        })


@is_enabled('chapters')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="chapters/edit-meta.html"):
    """
    Return chapter that allows you to edit meta-html information.
    """

    # check permission
    chapter = get_object_or_404(Chapter, pk=id)
    if not has_perm(request.user, 'chapters.change_chapter', chapter):
        raise Http403

    EventLog.objects.log(instance=chapter)

    defaults = {
        'title': chapter.get_title(),
        'description': chapter.get_description(),
        'keywords': chapter.get_keywords(),
        'canonical_url': chapter.get_canonical_url(),
    }
    chapter.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=chapter.meta)
        if form.is_valid():
            chapter.meta = form.save()  # save meta
            chapter.save()  # save relationship

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % chapter)

            return HttpResponseRedirect(reverse('chapters.detail', args=[chapter.slug]))
    else:
        form = form_class(instance=chapter.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'chapter': chapter, 'form': form})


@is_enabled('chapters')
@login_required
def delete(request, id, template_name="chapters/delete.html"):
    chapter = get_object_or_404(Chapter, pk=id)

    if not has_perm(request.user, 'chapters.delete_chapter'):
        raise Http403

    if request.method == "POST":
        EventLog.objects.log(instance=chapter)
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % chapter)

        # send notification to administrators
        recipients = get_notice_recipients('module', 'chapters', 'chapterrecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': chapter,
                    'request': request,
                }
                notification.send_emails(recipients, 'chapter_deleted', extra_context)

        chapter.delete()
        return HttpResponseRedirect(reverse('chapters.search'))

    return render_to_resp(request=request, template_name=template_name,
        context={'chapter': chapter})
