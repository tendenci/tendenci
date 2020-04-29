from builtins import str

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import template_exists, checklist_update
from tendenci.apps.base.views import file_display
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.versions.models import Version
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import (update_perms_and_save,
                                       get_notice_recipients,
                                       has_perm,
                                       has_view_perm,
                                       get_query_filters)
from tendenci.apps.categories.forms import CategoryForm
from tendenci.apps.categories.models import Category
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task
from tendenci.apps.notifications import models as notification

from tendenci.apps.pages.models import Page, HeaderImage
from tendenci.apps.pages.forms import PageForm
from tendenci.apps.categories.models import CategoryItem
from tendenci.apps.perms.utils import assign_files_perms


@is_enabled('pages')
def index(request, slug=None, id=None, hash=None,
          template_name="pages/view.html"):
    """
    Return page object, either as an archive, active, or version.
    """
    if not slug and not id and not hash:
        return HttpResponseRedirect(reverse('page.search'))

    if hash:
        version = get_object_or_404(Version, hash=hash)
        current_page = get_object_or_404(Page, pk=version.object_id)
        page = version.get_version_object()
        msg_string = 'You are viewing a previous version of this article. View the ' + \
         '<a href="%s">Current Version</a>.' % current_page.get_absolute_url()
        messages.add_message(request, messages.WARNING, _(msg_string))
    elif id:
        page = get_object_or_404(Page, pk=id)
        if page.status_detail != 'active':
            if not request.user.is_authenticated:
                pages = Page.objects.filter(
                    slug=page.slug, status_detail='active'
                ).order_by('-pk')
                if not pages:
                    pages = Page.objects.filter(slug=slug).order_by('-pk')
                if not pages:
                    raise Http404
                return HttpResponseRedirect(reverse('page', args=[page.slug]))

    else:
        try:
            page = get_object_or_404(Page, slug=slug)
        except Page.MultipleObjectsReturned:
            pages = Page.objects.filter(
                slug=slug, status_detail='active'
            ).order_by('-pk')
            if not pages:
                pages = Page.objects.filter(slug=slug).order_by('-pk')
            if not pages:
                raise Http404

            page = pages[0]

    if not has_view_perm(request.user, 'pages.view_page', page):
        raise Http403

    if not page.template or not template_exists(page.template):
        page.template = "pages/base.html"

    EventLog.objects.log(instance=page)

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page})


@is_enabled('pages')
def search(request, template_name="pages/search.html"):
    """
    Search pages.
    """
    query = request.GET.get('q')

    filters = get_query_filters(request.user, 'pages.view_page')
    pages = Page.objects.filter(filters).distinct()
    if query:
        if "category:" in query or "sub_category:" in query:
            # handle category and sub_category
            key, name = query.split(':', 1)
            categories = Category.objects.filter(name__iexact=name)
            if categories.exists():
                category = categories[0]
                if key == 'category':
                    page_ids = CategoryItem.objects.filter(content_type_id=ContentType.objects.get_for_model(Page), category_id=category.id, parent_id__isnull=True).values_list('object_id', flat=True)
                else:
                    page_ids = CategoryItem.objects.filter(content_type_id=ContentType.objects.get_for_model(Page), parent_id=category.id, category_id__isnull=True).values_list('object_id', flat=True)
                pages = pages.filter(id__in=page_ids)
            else:
                pages = Page.objects.none()

        else:
            pages = pages.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(slug__icontains=query))
            pages = pages.exclude(status_detail='archive')

    pages = pages.order_by('-create_dt')

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'pages': pages})


@is_enabled('pages')
def print_view(request, slug, template_name="pages/print-view.html"):
    try:
        page = get_object_or_404(Page, slug=slug)
    except Page.MultipleObjectsReturned:
        pages = Page.objects.filter(
            slug=slug, status_detail='active'
        ).order_by('-pk')
        if not pages:
            pages = Page.objects.filter(slug=slug).order_by('-pk')
        if not pages:
            raise Http404

        page = pages[0]

    if not has_perm(request.user, 'pages.view_page', page):
        raise Http403

    EventLog.objects.log(instance=page)

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page})


@is_enabled('pages')
@login_required
def edit(request, id, form_class=PageForm,
         meta_form_class=MetaForm,
         category_form_class=CategoryForm, template_name="pages/edit.html"):
    page = get_object_or_404(Page, pk=id)

    if not has_perm(request.user, 'pages.change_page', page):
        raise Http403

    content_type = get_object_or_404(ContentType, app_label='pages',
                                     model='page')

    if request.method == "POST":
        form = form_class(request.POST, request.FILES,
                          instance=page,
                          user=request.user)
        metaform = meta_form_class(request.POST,
                                   instance=page.meta,
                                   prefix='meta')
        categoryform = category_form_class(content_type,
                                           request.POST,)
        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            page = form.save()

            # handle header image
            f = form.cleaned_data['header_image']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get_for_model(Page)
                header.object_id = page.id
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                f.file.seek(0)
                header.file.save(filename, f)
                page.header_image = header

            #save meta
            meta = metaform.save()
            page.meta = meta

            ## update the category and subcategory
            page.update_category_subcategory(
                            categoryform.cleaned_data['category'],
                            categoryform.cleaned_data['sub_category']
                            )

            # update all permissions
            page = update_perms_and_save(request, form, page)
            if page.pk == 1:  # the about page has id 1 in the npo defaults fixture
                checklist_update('update-about')

            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully updated %(p)s' % {'p': str(page)}))

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module', 'pages',
                                                   'pagerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': page,
                            'request': request,
                        }
                        notification.send_emails(recipients,
                                                 'page_edited',
                                                 extra_context)

            return HttpResponseRedirect(reverse('page', args=[page.slug]))
    else:
        form = form_class(instance=page, user=request.user)
        metaform = meta_form_class(instance=page.meta, prefix='meta')
        #setup categories
        category = Category.objects.get_for_object(page, 'category')
        sub_category = Category.objects.get_for_object(page, 'sub_category')

        initial_category_form_data = {
            'app_label': 'pages',
            'model': 'page',
            'pk': page.pk,
            'category': getattr(category, 'name', '0'),
            'sub_category': getattr(sub_category, 'name', '0')
        }

        categoryform = category_form_class(content_type,
                                           initial=initial_category_form_data,)

    return render_to_resp(request=request, template_name=template_name,
        context={
            'page': page,
            'form': form,
            'metaform': metaform,
            'categoryform': categoryform,
        })


@is_enabled('pages')
@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="pages/edit-meta.html"):
    """
    Return page that allows you to edit meta-html information.
    """
    # check permission
    page = get_object_or_404(Page, pk=id)
    if not has_perm(request.user, 'pages.change_page', page):
        raise Http403

    defaults = {
        'title': page.get_title(),
        'description': page.get_description(),
        'keywords': page.get_keywords(),
        'canonical_url': page.get_canonical_url(),
    }
    page.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=page.meta)
        if form.is_valid():
            page.meta = form.save()  # save meta
            page.save()  # save relationship

            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully updated meta for %(p)s' % {'p': str(page)}))

            return HttpResponseRedirect(reverse('page', args=[page.slug]))
    else:
        form = form_class(instance=page.meta)

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page, 'form': form})


@login_required
def preview(request, id=None, form_class=PageForm, meta_form_class=MetaForm,
        category_form_class=CategoryForm, template="pages/preview.html"):

    content_type = get_object_or_404(ContentType,
                                     app_label='pages',
                                     model='page')
    page = None
    if id:
        page = get_object_or_404(Page, pk=id)

    if request.method == "POST":
        if page:
            form = form_class(request.POST, request.FILES, instance=page, user=request.user)
        else:
            form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type,
                                           request.POST,
                                           prefix='category')
        if form.is_valid():
            page = form.save(commit=False)

            edit_button = False
            if request.POST.get('preview_for', '') == 'edit':
                edit_button = True

            f = form.cleaned_data['header_image']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get_for_model(Page)
                header.object_id = page.id
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                f.file.seek(0)
                header.file.save(filename, f, save=False)
                page.header_image = header

            if 'preview_for' not in request.POST:
                page.save()
 
                if metaform.is_valid():
                    #save meta
                    meta = metaform.save()
                    page.meta = meta

                if categoryform.is_valid():
                    ## update the category and subcategory
                    page.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

                # update all permissions
                page = update_perms_and_save(request, form, page)

                messages.add_message(request, messages.SUCCESS,
                                 _('Successfully updated %(p)s' % {'p': str(page)}))
                if not request.user.profile.is_superuser:
                    # send notification to administrators
                    recipients = get_notice_recipients('module', 'pages',
                                                       'pagerecipients')
                    if recipients:
                        if notification:
                            extra_context = {
                                'object': page,
                                'request': request,
                            }
                            notification.send_emails(recipients,
                                                     'page_edited',
                                                     extra_context)
    
                return HttpResponseRedirect(reverse('page', args=[page.slug]))

            return render_to_resp(request=request, template_name=template,
               context={'page': page,
                                                'form': form,
                                                'metaform': metaform,
                                                'categoryform': categoryform,
                                                'edit_button': edit_button})

    return HttpResponseRedirect(reverse('page.search'))


@is_enabled('pages')
@login_required
def add(request, form_class=PageForm, meta_form_class=MetaForm,
        category_form_class=CategoryForm,
        template_name="pages/add.html"):
    if not has_perm(request.user, 'pages.add_page'):
        raise Http403

    content_type = get_object_or_404(ContentType,
                                     app_label='pages',
                                     model='page')

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type,
                                           request.POST,)
        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            page = form.save(commit=False)
            # add all permissions and save the model
            page = update_perms_and_save(request, form, page)

            # handle header image
            f = form.cleaned_data['header_image']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get_for_model(Page)
                header.object_id = page.id
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                f.file.seek(0)
                header.file.save(filename, f)
                page.header_image = header
                page.save()
                assign_files_perms(page, files=[page.header_image])

            #save meta
            meta = metaform.save()
            page.meta = meta

            ## update the category and subcategory
            page.update_category_subcategory(
                                    categoryform.cleaned_data['category'],
                                    categoryform.cleaned_data['sub_category']
                                    )

            messages.add_message(request, messages.SUCCESS,
                                 _('Successfully added %(p)s' % {'p': str(page)}))

            checklist_update('add-page')

            if not request.user.profile.is_superuser:
                # send notification to administrators
                recipients = get_notice_recipients('module',
                                                   'pages',
                                                    'pagerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': page,
                            'request': request,
                        }
                        notification.send_emails(recipients, 'page_added', extra_context)
            if page.status and page.status_detail == 'active':
                return HttpResponseRedirect(reverse('page', args=[page.slug]))
            return HttpResponseRedirect(reverse('page.search'))
    else:
        initial_category_form_data = {
            'app_label': 'pages',
            'model': 'page',
            'pk': 0,
        }
        form = form_class(user=request.user)
        metaform = meta_form_class(prefix='meta')
        categoryform = category_form_class(content_type,
                                           initial=initial_category_form_data,)
    return render_to_resp(request=request, template_name=template_name,
            context={
                'form': form,
                'metaform': metaform,
                'categoryform': categoryform,
            })


@is_enabled('pages')
@login_required
def delete(request, id, template_name="pages/delete.html"):
    page = get_object_or_404(Page, pk=id)

    if not has_perm(request.user, 'pages.delete_page'):
        raise Http403

    if request.method == "POST":
        EventLog.objects.log(instance=page)
        messages.add_message(request, messages.SUCCESS,
                             _('Successfully deleted %(p)s' % { 'p': str(page)}))

        # send notification to administrators
        recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': page,
                    'request': request,
                }
                notification.send_emails(recipients, 'page_deleted', extra_context)

        # Soft delete
        page.status = False
        page.status_detail = 'inactive'
        page.save()
        return HttpResponseRedirect(reverse('page.search'))

    return render_to_resp(request=request, template_name=template_name,
        context={'page': page})


@is_enabled('pages')
def display_header_image(request, id):
    page = get_object_or_404(Page, pk=id)

    if not has_view_perm(request.user,
                        '[pages.view_page',
                        page):
        raise Http403

    return file_display(request, page.header_image.file.name)


@is_enabled('pages')
@login_required
def export(request, template_name="pages/export.html"):
    """Export Pages"""
    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':

        fields = [
            'guid',
            'title',
            'slug',
            'header_image',
            'content',
            'view_contact_form',
            'design_notes',
            'syndicate',
            'template',
            'tags',
            'entity',
            'meta',
            'categories',
        ]

        export_id = run_export_task('pages', 'page', fields)
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
