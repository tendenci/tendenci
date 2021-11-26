from functools import reduce
import operator
import simplejson
from datetime import date
import time as ttime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.urls import reverse
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.forms.models import modelformset_factory
from django.utils.translation import gettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.meta.forms import MetaForm
from tendenci.apps.categories.forms import CategoryForm
from tendenci.apps.categories.models import Category
from tendenci.apps.files.models import File
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.chapters.models import (Chapter, Officer,
                                           ChapterMembershipAppField,
                                           ChapterMembershipApp,
                                           ChapterMembership,
                                           Notice)
from tendenci.apps.chapters.forms import (ChapterForm, OfficerForm,
                                          OfficerBaseFormSet,
                                          ChapterSearchForm,
                                          AppFieldCustomForm,
                                          AppFieldBaseFormSet,
                                          ChapterMembershipForm,
                                          ChapterMemberSearchForm)
from tendenci.apps.perms.utils import update_perms_and_save, get_notice_recipients, has_perm, get_query_filters
from tendenci.apps.perms.fields import has_groups_perms
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.notifications import models as notification
from tendenci.apps.base.utils import Echo
from tendenci.apps.chapters.utils import get_chapter_membership_field_values


@is_enabled('chapters')
def detail(request, slug, template_name="chapters/detail.html"):
    chapter = get_object_or_404(Chapter, slug=slug)

    if has_perm(request.user, 'chapters.view_chapter', chapter) \
            or chapter.is_chapter_leader(request.user):
        EventLog.objects.log(instance=chapter)
        officers = chapter.officers().filter(Q(expire_dt__isnull=True) | Q(expire_dt__gte=date.today()))

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
        show_officers_phone = officers.exclude(phone__isnull=True).exclude(phone='').exists()
        show_officers_email = officers.exclude(email__isnull=True).exclude(email='').exists()

        return render_to_resp(request=request, template_name=template_name,
            context={
                'chapter': chapter,
                'officers': officers,
                'files': files,
                'has_group_view_permission': has_group_view_permission,
                'show_officers_phone': show_officers_phone,
                'show_officers_email': show_officers_email,
                'is_chapter_member': chapter.is_chapter_member(request.user)
            })
    else:
        if chapter.status_detail.lower() == 'pending':
            placeholder = get_setting('module', 'chapters', 'pendingplaceholder')
            if placeholder:
                return HttpResponseRedirect(placeholder)
        raise Http403


@is_enabled('chapters')
def search(request, template_name="chapters/search.html"):
    form = ChapterSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('q')
        region = form.cleaned_data.get('region')
        state = form.cleaned_data.get('state')
        county = form.cleaned_data.get('county')
        
        if query:
            chapters = Chapter.objects.search(query, user=request.user)
        else:
            filters = get_query_filters(request.user, 'chapters.view_chapter')
            chapters = Chapter.objects.filter(filters).distinct()

        if region:
            chapters = chapters.filter(region=region)
        if state:
            chapters = chapters.filter(state=state)
        if county:
            chapters = chapters.filter(county__iexact=county)
        chapters = chapters.order_by('-create_dt')
    else:
        chapters = Chapter.objects.none()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'chapters': chapters,
                 'form': form})


@is_enabled('chapters')
@login_required
def add(request, copy_from_id=None, form_class=ChapterForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="chapters/add.html"):

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
        chapter_initial = {}
        if copy_from_id:
            try:
                copy_from_id = int(copy_from_id)
            except (ValueError, TypeError):
                copy_from_id = None
            if copy_from_id and Chapter.objects.filter(id=copy_from_id).exists():
                copy_from_chapter = Chapter.objects.get(id=copy_from_id)
                # they can't copy if they don't have the view perm of the copy_from_chapter
                if has_perm(request.user, 'chapters.view_chapter', copy_from_chapter):
                    for field in copy_from_chapter._meta.fields:
                        if field.name in ('title', 'slug', 'content', 'view_contact_form',
                                          'design_notes', 'syndicate', 'template', 'tags',
                                          'mission', 'notes', 'sponsors', 'contact_name',
                                          'contact_email', 'join_link', 'region',
                                          'county', 'state',):
                            chapter_initial[field.name] = getattr(copy_from_chapter, field.name)
                    chapter_initial['title'] = f"Copy of {chapter_initial['title']}"
                    chapter_initial['slug'] = f"copy-{chapter_initial['slug']}"
        form = form_class(user=request.user, initial=chapter_initial)
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

    if not (has_perm(request.user,'chapters.change_chapter',chapter) \
            or chapter.is_chapter_leader(request.user)):
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

            # update group perms to officers
            chapter.update_group_perms()

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
    if not (has_perm(request.user, 'chapters.change_chapter', chapter) \
            or chapter.is_chapter_leader(request.user)):
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


@is_enabled('chapters')
@login_required
def chapter_memberships_search(request, chapter_id=0,
                               template_name="chapters/memberships/search.html"):
    if chapter_id:
        chapter = get_object_or_404(Chapter, pk=chapter_id)
    else:
        chapter = None

    app = ChapterMembershipApp.objects.current_app()
    if not app:
        raise Http404

    if not (has_perm(request.user, 'chapters.change_chaptermembership') or \
            (chapter and chapter.is_chapter_leader(request.user))):
        raise Http403
    chapter_memberships = ChapterMembership.objects.filter(app_id=app.id
                                    ).exclude(status_detail__in=['archive', 'inactive', 'admin_hold'])
    if chapter:
        chapter_memberships = chapter_memberships.filter(chapter=chapter)
    app_fields = app.fields.filter(display=True).exclude(
            field_name__in=['payment_method',
                            'membership_type',
                            'groups',
                            'status',
                            'status_detail',
                            ''])
    form = ChapterMemberSearchForm(request.GET, app_fields=app_fields,
                                   user=request.user, chapter=chapter)
    if form.is_valid():
        membership_fieldnames = [field.name for field in ChapterMembership._meta.fields if \
                           field.get_internal_type() in ['CharField', 'TextField']]
        chapter_selected = form.cleaned_data.get('chapter', None)
        membership_type = form.cleaned_data.get('membership_type')
        payment_status = form.cleaned_data.get('payment_status')
        status_detail = form.cleaned_data.get('status_detail')
        if chapter_selected:
            chapter_memberships = chapter_memberships.filter(chapter__id=chapter_selected)
        if membership_type:
            chapter_memberships = chapter_memberships.filter(membership_type__id=membership_type)
        if payment_status == 'paid':
            chapter_memberships = chapter_memberships.filter(invoice__balance__lte=0)
        elif payment_status == 'not_paid':
            chapter_memberships = chapter_memberships.filter(invoice__balance__gt=0)
        if status_detail:
            chapter_memberships = chapter_memberships.filter(status_detail__iexact=status_detail)
        for field_name, field_value in form.cleaned_data.items():
            if field_value:
                if isinstance(field_value, list):
                    if field_name in membership_fieldnames:
                        chapter_memberships = chapter_memberships.filter(reduce(operator.or_, 
                            [Q(**{f'{field_name}__icontains': value}) for value in field_value]))
                elif isinstance(field_value, str):
                    if field_name in membership_fieldnames:
                        chapter_memberships = chapter_memberships.filter(Q(**{f'{field_name}__icontains': field_value}))
    chapter_memberships = chapter_memberships.order_by('user__last_name', 'user__first_name')

    if 'export' in request.GET:
        EventLog.objects.log(description="chapter memberships export")
        import csv
        def iter_chapter_memberships(chapter_memberships, app_fields):
            field_labels = [field.label for field in app_fields]
            field_labels += [_('Create Date'), _('Join Date'), _('Renew Date'),
                            _('Expire Date'), _('Status Detail')]
            field_labels.insert(0, _('Chapter'))
            
            writer = csv.DictWriter(Echo(), fieldnames=field_labels)
            # write headers - labels
            yield writer.writerow(dict(zip(field_labels, field_labels)))
        
            for chapter_membership in chapter_memberships:
                values_list = get_chapter_membership_field_values(chapter_membership, app_fields)
                if chapter_membership.create_dt:
                    values_list.append(chapter_membership.create_dt.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    values_list.append('')
                if chapter_membership.join_dt:
                    values_list.append(chapter_membership.join_dt.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    values_list.append('')
                if chapter_membership.renew_dt:
                    values_list.append(chapter_membership.renew_dt.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    values_list.append('')
                if chapter_membership.expire_dt:
                    values_list.append(chapter_membership.expire_dt.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    values_list.append('')
                values_list.append(chapter_membership.status_detail)
                
                values_list.insert(0, chapter_membership.chapter.title)
        
                yield writer.writerow(dict(zip(field_labels, values_list)))

        response = StreamingHttpResponse(
        streaming_content=(iter_chapter_memberships(chapter_memberships, app_fields)),
        content_type='text/csv',)
        response['Content-Disposition'] = f'attachment;filename=chapter_memberships_export_{ttime.time()}.csv'
        return response

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={
            'chapter_memberships': chapter_memberships,
            'search_form': form,
            'app': app,
            'chapter': chapter,
            'app_fields': app_fields})


@csrf_exempt
@staff_member_required
def get_app_fields_json(request):
    """
    Get the app fields and return as json
    """
    complete_list = simplejson.loads(
        render_to_string(template_name='chapters/app_fields.json'))
    return HttpResponse(simplejson.dumps(complete_list), content_type="application/json")


@is_enabled('chapters')
@login_required
def edit_app_fields(request, id, form_class=AppFieldCustomForm, template_name="chapters/edit_app_fields.html"):
    chapter = get_object_or_404(Chapter, pk=id)

    if not has_perm(request.user, 'chapters.change_chaptermembershipappfield') \
            and not chapter.is_chapter_leader(request.user):
        raise Http403

    AppFieldFormSet = modelformset_factory(
        ChapterMembershipAppField,
        formset=AppFieldBaseFormSet,
        form=form_class,
        extra=0,
        can_delete=False
    )
    formset_app_fields = AppFieldFormSet(
            request.POST or None,
            queryset=ChapterMembershipAppField.objects.filter(
                customizable=True).exclude(field_name__in=['membership_type', 'payment_method']),
            prefix='app_field',
            form_kwargs={'chapter': chapter,}
        )
    if request.method == "POST":
        if formset_app_fields.is_valid():
            cfields = formset_app_fields.save()
            
            msg_string = _('Successfully saved fields: ') + \
                ', '.join([cfield.app_field.label for cfield in cfields])
            messages.add_message(request, messages.SUCCESS, _(msg_string))

            #TODO: redirect to application add

    # response
    return render_to_resp(request=request, template_name=template_name,
        context={'chapter': chapter, 'formset_app_fields': formset_app_fields,})


@is_enabled('chapters')
@login_required
def membership_details(request, chapter_membership_id=0,
                       template_name="chapters/memberships/details.html"):
    chapter_membership = get_object_or_404(ChapterMembership, id=chapter_membership_id)
    chapter = chapter_membership.chapter
    is_chapter_leader = chapter.is_chapter_leader(request.user)
    has_change_perm = has_perm(request.user, 'chapters.change_chaptermembership')
    has_approve_perm = is_chapter_leader or has_change_perm
    if not any((is_chapter_leader,
            request.user == chapter_membership.user,
            has_change_perm)):
        raise Http403

    if request.user.is_superuser or is_chapter_leader:
        if 'approve' in request.GET:
            chapter_membership.approve(request_user=request.user)
            #chapter_membership.send_email(request, ('approve_renewal' if chapter_membership.renewal else 'approve'))
            messages.add_message(request, messages.SUCCESS, _('Successfully Approved'))

        if 'disapprove' in request.GET:
            chapter_membership.disapprove(request_user=request.user)
            messages.add_message(request, messages.SUCCESS, _('Successfully Disapproved'))

        if 'expire' in request.GET:
            chapter_membership.expire(request_user=request.user)
            messages.add_message(request, messages.SUCCESS, _('Successfully Expired'))


    app = chapter_membership.app
    app_fields = app.fields.filter(display=True)
    if not (is_chapter_leader and request.user.is_superuser):
        app_fields = app_fields.filter(admin_only=False)

    if not has_perm(request.user, 'memberships.approve_membershipdefault'):
        app_fields = app_fields.filter(admin_only=False)

    app_fields = app_fields.order_by('position')

    # assign values
    for field in app_fields:
        field_name = field.field_name
        if field_name and hasattr(chapter_membership, field_name):
            field.value = getattr(chapter_membership, field_name)

    EventLog.objects.log(instance=chapter_membership)
    return render_to_resp(
        request=request, template_name=template_name, context={
            'chapter_membership': chapter_membership,
            'has_approve_perm': has_approve_perm,
            'app_fields': app_fields,
            'actions': chapter_membership.get_actions(request.user)
        })

@is_enabled('chapters')
@login_required
def chapter_membership_add(request, chapter_id=0,
                           template='chapters/applications/add.html', **kwargs):
    """
    Chapter membership application form.
    """
    # chapter membership add
    chapter_membership = None
    chapter = get_object_or_404(Chapter, id=chapter_id)
    app = ChapterMembershipApp.objects.current_app()

    if not has_perm(request.user, 'chapters.view_chaptermembershipapp', app):
        raise Http403

    edit_mode = False

    # app fields
    app_fields = app.get_app_fields(chapter, request.user)
    
    params = {
        'request_user': request.user,
        'is_renewal': False,
        'edit_mode': edit_mode,
        'app': app,
    }
    chapter_membership_form = ChapterMembershipForm(app_fields, chapter,
                            request.POST or None, instance=chapter_membership, **params)

    if request.method == 'POST':
        if chapter_membership_form.is_valid():
            # create a chapter membership
            chapter_membership = chapter_membership_form.save()
            # create an invoice
            chapter_membership.save_invoice()

            if chapter_membership.approval_required():
                # approval is required - set pending
                chapter_membership.pend()
                chapter_membership.save()

            # send notification to user
            chapter_membership.send_email(notice_type='apply')

            if not chapter_membership.approval_required():
                # not require approval - approve it!
                chapter_membership.approve(request_user=request.user)

            # add user to the newsletter group, if any
            if chapter.newsletter_group:
                chapter.newsletter_group.add_user(chapter_membership.user)

            # log an event
            EventLog.objects.log(instance=chapter_membership)
            
            # TODO: email notification to admin
            # Who should be notified? site admin or chapter leaders?

            # handle online payment
            if chapter_membership.payment_method.is_online and \
                    chapter_membership.invoice.balance > 0:
                return HttpResponseRedirect(
                                reverse('payment.pay_online',
                                args=[chapter_membership.invoice.id,
                                      chapter_membership.invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('chapters.membership_add_conf',
                                    args=[chapter_membership.id]))

#     captcha_form = CaptchaForm(request.POST or None)
#     if request.user.is_authenticated or not app.use_captcha:
#         del captcha_form.fields['captcha']

    app.render_items({'chapter': chapter})

    context = {
        'chapter': chapter,
        'app': app,
        'app_fields': app_fields,
        'chapter_membership_form': chapter_membership_form,
        'is_edit': False,
        'is_renewal': False,
    }
    return render_to_resp(request=request, template_name=template, context=context)


@is_enabled('chapters')
@login_required
def chapter_membership_edit(request, chapter_membership_id=0,
                           template='chapters/applications/add.html', **kwargs):
    """
    Chapter membership edit.
    """
    
    chapter_membership = get_object_or_404(ChapterMembership, id=chapter_membership_id)
    if not chapter_membership.allow_edit_by(request.user):
        raise Http403
    app = chapter_membership.app
    chapter = chapter_membership.chapter
    edit_mode = True

    # app fields
    app_fields = app.get_app_fields(chapter, request.user)
    
    params = {
        'request_user': request.user,
        'is_renewal': False,
        'edit_mode': edit_mode,
        'app': app,
    }
    chapter_membership_form = ChapterMembershipForm(app_fields, chapter,
                            request.POST or None, instance=chapter_membership, **params)

    if request.method == 'POST':
        if chapter_membership_form.is_valid():
            # save changes
            chapter_membership = chapter_membership_form.save()

            # log an event
            EventLog.objects.log(instance=chapter_membership)

            messages.success(request, _('Successfully updated Chapter Membership Information.'))
            return HttpResponseRedirect(reverse('chapters.membership_details',
                                args=[chapter_membership.id]))

    app.render_items({'chapter': chapter})

    context = {
        'chapter': chapter,
        'app': app,
        'app_fields': app_fields,
        'chapter_membership_form': chapter_membership_form,
        'is_edit': edit_mode,
        'is_renewal': False,
        'chapter_membership': chapter_membership
    }
    return render_to_resp(request=request, template_name=template, context=context)


@is_enabled('chapters')
@login_required
def chapter_membership_renew(request, chapter_membership_id=0,
                           template='chapters/applications/add.html', **kwargs):
    """
    Chapter membership renew.
    """
    chapter_membership = get_object_or_404(ChapterMembership, id=chapter_membership_id)
    if not chapter_membership.allow_edit_by(request.user):
        raise Http403

    if not chapter_membership.can_renew():
        return HttpResponseRedirect(reverse('chapters.membership_details',
                    args=[chapter_membership.id]))

    app = chapter_membership.app
    chapter = chapter_membership.chapter
    renew_from_id = chapter_membership.id
    
    # app fields
    app_fields = app.get_app_fields(chapter, request.user)
    membership_initial = {}
    for app_field in app_fields:
        field_name = app_field.field_name
        if field_name and hasattr(chapter_membership, field_name):
            membership_initial[field_name] = getattr(chapter_membership, field_name)
        
    
    params = {
        'request_user': request.user,
        'renew_from_id': renew_from_id,
        'is_renewal': True,
        'app': app,
    }
    chapter_membership_form = ChapterMembershipForm(app_fields, chapter,
                request.POST or None, initial=membership_initial, **params)
    if request.method == 'POST':
        if chapter_membership_form.is_valid():
            # create a chapter membership
            chapter_membership = chapter_membership_form.save()

            # create an invoice
            chapter_membership.save_invoice()
            if chapter_membership.approval_required():
                # approval is required - set pending
                chapter_membership.pend()
                chapter_membership.save()

            # send notification to user
            chapter_membership.send_email(notice_type='renewal')

            if not chapter_membership.approval_required():
                # not require approval - approve it!
                chapter_membership.approve(request_user=request.user)

            # log an event
            EventLog.objects.log(instance=chapter_membership)

            # TODO: email notification to admin
            # Who should be notified? site admin or chapter leaders?

            # handle online payment
            if chapter_membership.payment_method.is_online and \
                    chapter_membership.invoice.balance > 0:
                return HttpResponseRedirect(
                                reverse('payment.pay_online',
                                args=[chapter_membership.invoice.id,
                                      chapter_membership.invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('chapters.membership_add_conf',
                                    args=[chapter_membership.id]))

    app.render_items({'chapter': chapter})

    context = {
        'chapter': chapter,
        'app': app,
        'app_fields': app_fields,
        'chapter_membership_form': chapter_membership_form,
        'is_edit': False,
        'is_renewal': True,
        'chapter_membership': chapter_membership
    }
    return render_to_resp(request=request, template_name=template, context=context)


@is_enabled('chapters')
@login_required
def chapter_membership_add_conf(request, id,
            template="chapters/applications/add_conf.html"):
    """
        Chapter membership add conf
    """
    chapter_membership = get_object_or_404(ChapterMembership, id=id)
    app = chapter_membership.app
    app.render_items({'chapter': chapter_membership.chapter})

    EventLog.objects.log(instance=chapter_membership)

    context = {'app': app, "chapter_membership": chapter_membership}
    return render_to_resp(request=request, template_name=template, context=context)

