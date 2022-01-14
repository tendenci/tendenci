
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.shortcuts import redirect
from django.http.response import HttpResponseRedirect

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.chapters.models import (Chapter, Position, Officer,
                            ChapterMembershipType,
                            ChapterMembershipAppField,
                            ChapterMembershipApp,
                            ChapterMembership,
                            Notice,
                            NoticeLog,
                            NoticeDefaultLogRecord)
from tendenci.apps.chapters.forms import (ChapterAdminForm,
                        ChapterAdminChangelistForm,
                        UserModelChoiceField,
                        ChapterMembershipTypeForm,
                        ChapterMembershipAppForm,
                        ChapterMembershipAppFieldAdminForm,
                        NoticeForm)
from tendenci.apps.theme.templatetags.static import static
from tendenci.apps.base.utils import tcurrency


class ChapterMembershipTypeAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'price', 'require_approval',
                     'allow_renewal', 'renewal_price', 'renewal',
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price', 'status_detail']

    exclude = ('status',)

    fieldsets = (
        (None, {'fields': ('name', 'price', 'description')}),
        (_('Expiration Method'), {'fields': ('never_expires', 'type_exp_method',)}),
        (_('Renewal Options for this membership type'), {'fields': ('allow_renewal', 'renewal', 'renewal_require_approval',
                                        'renewal_price',
                                        'renewal_period_start',
                                        'renewal_period_end',)}),

        (_('Other Options'), {'fields': (
            'expiration_grace_period', 'require_approval',
            'admin_only', 'require_payment_approval', 'position', 'status_detail')}),
    )

    form = ChapterMembershipTypeForm
    ordering = ['position']

    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
              static('js/membtype.js'),)

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # save the expiration method fields
        type_exp_method = form.cleaned_data['type_exp_method']
        type_exp_method_list = type_exp_method.split(",")
        for i, field in enumerate(form.type_exp_method_fields):
            if field == 'fixed_option2_can_rollover':
                if type_exp_method_list[i] == '':
                    type_exp_method_list[i] = False
            else:
                if type_exp_method_list[i] == '':
                    type_exp_method_list[i] = "0"

            setattr(instance, field, type_exp_method_list[i])

        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

        # save the object
        instance.save()

        #form.save_m2m()

        return instance


class ChapterMembershipAppFieldAdmin(admin.TabularInline):
    model = ChapterMembershipAppField
    fields = ('label', 'field_name', 'display', 'required',
              'customizable', 'admin_only', 'position',)
#               'field_type', 'help_text', 'choices',
#               'default_value', 'css_class')
    extra = 0
    can_delete = False
    verbose_name = _('Section Break')
    ordering = ("position",)
    sortable_field_name = 'position'
    template = "chapters/admin/chaptermembershipapp/tabular.html"
    show_change_link = True


class ChapterMembershipAppAdmin(TendenciBaseModelAdmin):
    inlines = (ChapterMembershipAppFieldAdmin, )
    prepopulated_fields = {'slug': ['name']}
    list_display = ('id', 'name', 'status_detail', 'members_search_link')
    list_display_links = ('name',)
    search_fields = ('name', 'status_detail')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description',
                           'confirmation_text', 'renewal_description', 
                           'renewal_confirmation_text', 'notes',
                           'membership_types', 'payment_methods',
                           'use_captcha')},),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        (_('Status'), {'fields': (
            'status_detail',
        )}),
    )

    form = ChapterMembershipAppForm
    #change_form_template = "chapters/admin/chaptermembershipapp/change_form.html"

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/membapp_tabular_inline_ordering.js'),
            static('js/global/tinymce.event_handlers.js'),
        )
        css = {'all': [static('css/admin/dynamic-inlines-with-sort.css'),
                       static('css/memberships-admin.css')], }

    def add_view(self, request):
        if ChapterMembershipApp.objects.all().count() >=1:
            messages.add_message(
            request,
            messages.ERROR,
            _('Currently support one application ONLY.'))
            
            return redirect(reverse(
                'admin:chapters_chaptermembershipapp_changelist',
            ))
        return super(ChapterMembershipAppAdmin, self).add_view(request)

    @mark_safe
    def members_search_link(self, instance):
        return '<a href="%s" title="%s"><i class="glyphicon glyphicon-search"></i> Search Chapter Members</a>' % (
                reverse('chapters.memberships_search'),
                        _('Search Chapter Members'))
    members_search_link.short_description = _('Chapter Members Search Link')


class AppListFilter(SimpleListFilter):
    title = _('Chapter Membership App')
    parameter_name = 'membership_app_id'

    def lookups(self, request, model_admin):
        apps_list = ChapterMembershipApp.objects.filter(
                        status=True,
                        status_detail__in=['active', 'published']
                        ).values_list('id', 'name'
                        ).order_by('id')
        return [(app_tuple[0], app_tuple[1]) for app_tuple in apps_list]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(
                    membership_app_id=int(self.value()))
        queryset = queryset.filter(display=True)
        return queryset


class ChapterMembershipAppField2Admin(admin.ModelAdmin):
    model = ChapterMembershipAppField
    list_display = ['id', 'edit_link', 'label', 'field_name', 'app_id', 'display',
              'required', 'customizable', 'admin_only', 'position',
              ]
    list_display_links = ('edit_link',)

    readonly_fields = ('membership_app', 'field_name')

    list_editable = ['position']
    ordering = ("position",)
    list_filter = (AppListFilter,)
    form = ChapterMembershipAppFieldAdminForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
        )

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = _('edit')

    def app_id(self, obj):
        return obj.membership_app.id
    app_id.short_description = _('App ID')

    def get_fieldsets(self, request, obj=None):
        extra_fields = ['description', 'help_text',
                        'choices', 'default_value', 'css_class']
        if obj:
            if obj.field_name:
                extra_fields.remove('description')
            else:
                extra_fields.remove('help_text')
                extra_fields.remove('choices')
                extra_fields.remove('default_value')
        fields = ('membership_app', 'label', 'field_name', 'field_type',
                    'display', 'required', 'customizable', 'admin_only',
                             ) + tuple(extra_fields)

        return ((None, {'fields': fields
                        }),)

    def get_object(self, request, object_id, from_field=None):
        obj = super(ChapterMembershipAppField2Admin, self).get_object(request, object_id)

        # assign default field_type
        if obj:
            if not obj.field_type:
                if not obj.field_name:
                    obj.field_type = 'section_break'
                else:
                    obj.field_type = ChapterMembershipAppField.get_default_field_type(obj.field_name)

        return obj

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        return super(ChapterMembershipAppField2Admin, self).change_view(request, object_id, form_url,
                               extra_context=dict(show_delete=False))

#     def has_delete_permission(self, request, obj=None):
#         return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        return None


class PaymentStatusFilter(admin.SimpleListFilter):
    title = _('Payment Status')
    parameter_name = 'paid'

    def lookups(self, request, model_admin):
        return (
                ('1', _('Paid')),
                ('0', _('Not Paid')))

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        else:
            if value == '1':
                return queryset.filter(invoice__balance__lte=0)
            else:
                return queryset.filter(invoice__balance__gt=0)


class ChapterMembershipAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'view_on_site',
                    'user_link',
                    'chapter_link',
                    'm_type',
                    'approved',
                    'join_date', 
                    'renewal',
                    'renew_date',
                    'expire_date',
                    'status_detail',
                    'invoice_url',
                    'paid',]
    list_filter = ['membership_type', 'status_detail', 'renewal', PaymentStatusFilter]
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'chapter__title')

    def get_queryset(self, request):
        """
        Excludes archive
        """
        return super(ChapterMembershipAdmin, self).get_queryset(request
                    ).exclude(status_detail='archive'
                              ).filter(status=True).order_by('-create_dt')

#     @mark_safe
#     def edit_link(self, instance):
#         return '<a href="%s" title="edit chapter membership">%s</a>' % (
#                 reverse('chapters.membership_edit',args=[instance.id]),
#                 _('Edit'),)
#     edit_link.short_description = _('edit')
    
    @mark_safe
    def view_on_site(self, obj):
        if not hasattr(obj, 'get_absolute_url'):
            return None

        link_icon = static('images/icons/external_16x16.png')
        link = '<a href="%s" title="%s"><img src="%s" alt="view chapter membership" title="view chapter membership"/></a>' % (
            obj.get_absolute_url(),
            strip_tags(obj),
            link_icon,
        )
        return link
    view_on_site.short_description = _('view')

    def paid(self, instance):
        if instance.invoice:
            return instance.invoice.balance <= 0
    paid.boolean = True

    @mark_safe
    def user_link(self, instance):
        if instance.user:
            profile_url = reverse('profile',
                      args=[instance.user.username])
            name = instance.user.get_full_name()
            if name:
                return f'<a href="{profile_url}">{name}</a>'
            return f'<a href="{profile_url}">{instance.user.username}</a>'
 
        return "-"
    user_link.short_description = _('User')
    user_link.allow_tags = True
    user_link.admin_order_field = 'user'

    @mark_safe
    def chapter_link(self, instance):
        chapter_url = reverse('chapters.detail',
                  args=[instance.chapter.slug])
        return f'<a href="{chapter_url}">{instance.chapter.title}</a>'

    chapter_link.short_description = _('Chapter')
    chapter_link.allow_tags = True
    chapter_link.admin_order_field = 'chapter'

    @mark_safe
    def invoice_url(self, instance):
        invoice = instance.invoice
        if invoice:
            if invoice.balance > 0:
                return f'<a href="{invoice.get_absolute_url()}">Invoice {invoice.pk} ({tcurrency(invoice.balance)})</a>' 
            else:
                return f'<a href="{invoice.get_absolute_url()}">Invoice {invoice.pk}</a>'
        return ""
    invoice_url.short_description = 'Invoice'

    @mark_safe
    def m_type(self, instance):
        if not instance.membership_type:
            return ''
        mtype_url = reverse('admin:chapters_chaptermembershiptype_change',
                      args=[instance.membership_type.id])
        return f'<a href="{mtype_url}">{instance.membership_type.name}</a>'
    m_type.short_description = _('Membership Type')
    m_type.admin_order_field = 'membership_type'
    
    def join_date(self, instance):
        if not instance.join_dt:
            return ''
        return instance.join_dt.strftime('%m-%d-%Y')
    join_date.short_description = _('Join Date')
    join_date.admin_order_field = 'join_dt'

    def renew_date(self, instance):
        if not instance.renew_dt:
            return ''
        return instance.renew_dt.strftime('%m-%d-%Y')
    renew_date.short_description = _('Renew Date')
    renew_date.admin_order_field = 'renew_dt'

    def expire_date(self, instance):
        if not instance.expire_dt:
            return ''
        return instance.expire_dt.strftime('%m-%d-%Y')
    expire_date.short_description = _('Expire Date')
    expire_date.admin_order_field = 'expire_dt'

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='',
                    extra_context=None):
        return HttpResponseRedirect(reverse('chapters.membership_edit',
                                            args=[object_id]))


class NoticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'notice_name', 'notice_logs', 'content_type',
                    'chapter', 'membership_type', 'status', 'status_detail']
    list_display_links = ('notice_name',)
    list_filter = ['notice_type', 'status_detail']

    fieldsets = (
        (None, {'fields': ('notice_name', 'notice_time_type', 'chapter', 'membership_type')}),
        (_('Email Fields'), {'fields': ('subject', 'content_type', 'sender', 'sender_display', 'email_content')}),
        (_('Other Options'), {'fields': ('status', 'status_detail')}),
    )

    form = NoticeForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            static('js/global/tinymce.event_handlers.js'),
            static('js/admin/membnotices.js'),
        )

    @mark_safe
    def notice_logs(self, obj):
        logs_url = reverse('admin:chapters_noticelog_changelist')
        return f'<a href="{logs_url}?notice__id__exact={obj.id}">View logs</a>' 

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        notice_time_type = form.cleaned_data['notice_time_type']
        notice_time_type_list = notice_time_type.split(",")
        instance.num_days = notice_time_type_list[0]
        instance.notice_time = notice_time_type_list[1]
        instance.notice_type = notice_time_type_list[2]

        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

        instance.save()

        return instance


class NoticeLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'show_notice', 'log_records', 'notice_sent_dt', 'num_sent']
    list_filter = ['notice',]
    can_delete = False
    search_fields = ['notice__notice_name']

    @mark_safe
    def show_notice(self, obj):
        notice_url = reverse('admin:chapters_notice_change', args=[obj.notice.id])
        return f'<a href="{notice_url}">{obj.notice.notice_name}</a>'
    show_notice.short_description = 'Notice'
    show_notice.allow_tags = True
    show_notice.admin_order_field = 'obj.notice.notice_name'

    @mark_safe
    def log_records(self, obj):
        logs_url = reverse('admin:chapters_noticedefaultlogrecord_changelist')
        return f'<a href="{logs_url}?notice_log__id__exact={obj.id}">View log records</a>' 

    def get_actions(self, request):
        return None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

class NoticeDefaultLogRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'show_notice', 'chapter_membership', 'emails_sent', 'sent_date']
    list_filter = ['notice_log__notice',]
    can_delete = False

    @mark_safe
    def show_notice(self, obj):
        notice_url = reverse('admin:chapters_notice_change', args=[obj.notice_log.notice.id])
        return f'<a href="{notice_url}">{obj.notice_log.notice.notice_name}</a>'
    show_notice.short_description = 'Notice'
    show_notice.allow_tags = True
    
    def sent_date(self, obj):
        return obj.create_dt
    sent_date.short_description = 'Sent date'
    sent_date.admin_order_field = 'create_dt'
    
    def get_actions(self, request):
        return None

    def has_add_permission(self, request):
        return False

#     def has_delete_permission(self, request, obj=None):
#         return False
    
    def has_change_permission(self, request, obj=None):
        return False


class OfficerAdminInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': (
            'position',
            'user',
            'phone',
            'email',
            'expire_dt'
        )},),
    )
    extra = 0
    model = Officer

    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'user':

            chapter = None
            chapter = self.get_object(kwargs['request'], Chapter)
            if chapter:
                return UserModelChoiceField(queryset=User.objects.filter(group_member__group=chapter.group), label="User")
            return UserModelChoiceField(queryset=User.objects.none(), label="User")
        return super(OfficerAdminInline, self).formfield_for_dbfield(field, **kwargs)

    def get_object(self, request, model):
        object_id = request.resolver_match.kwargs.get('object_id', None)
        if object_id:
            return model.objects.get(pk=object_id)
        return None


class ChapterAdmin(TendenciBaseModelAdmin):
    list_display = ('view_on_site', 'edit_link', 'title', 'group_link', 'newsletter_group_link', 'entity', 'admin_perms', 'admin_status')
    search_fields = ('title', 'content',)
    list_editable = ('title',)
    fieldsets = (
        (None, {'fields': (
            'title',
            'slug',
            'newsletter_group',
            'region',
            'state',
            'county',
            'mission',
            'content',
            'notes',
            'photo_upload',
            'contact_name',
            'contact_email',
            'join_link',
            'tags'
        )}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'syndicate',
            'status_detail'
        )}),
    )
    prepopulated_fields = {'slug': ['title']}
    form = ChapterAdminForm
    inlines = (OfficerAdminInline,)

    class Media:
        js = (
            static('js/global/tinymce.event_handlers.js'),
        )

    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(ChapterAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_changelist_form(self, request, **kwargs):
        """
        Returns a Form class for use in the Formset on the changelist page.
        We return our custom form to filter out inactive groups.
        """
        return ChapterAdminChangelistForm
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance)

        # save photo
        if 'photo_upload' in form.cleaned_data:
            photo = form.cleaned_data['photo_upload']
            if photo:
                instance.save(photo=photo)

        return instance

    def save_related(self, request, form, formsets, change):
        super(ChapterAdmin, self).save_related(request, form, formsets, change)
        # update group perms to officers
        form.instance.update_group_perms()


    def save_formset(self, request, form, formset, change):
        """
        Associate the user to each instance saved.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            instance.content_type = ContentType.objects.get_for_model(instance.chapter)
            instance.object_id = instance.chapter.pk
            instance.creator = request.user
            instance.owner = request.user
            instance.save()

    @mark_safe
    def link(self, obj):
        return '<a href="%s" title="%s">%s</a>' % (
            obj.get_absolute_url(),
            obj.title,
            obj.slug
        )

    @mark_safe
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:chapters_chapter_change', args=[obj.pk])
        return link
    edit_link.short_description = 'edit'
    
    @mark_safe
    def group_link(self, instance):
        group_url = reverse('group.detail',args=[instance.group.slug])
        group_name = instance.group.name
                            
        return f'<a href="{group_url}" title="{group_name}">{group_name}</a>'
    group_link.short_description = _('group')
    group_link.admin_order_field = 'group'
    
    @mark_safe
    def newsletter_group_link(self, instance):
        if instance.newsletter_group:
            group_url = reverse('group.detail',args=[instance.newsletter_group.slug])
            group_name = instance.newsletter_group.name
                                
            return f'<a href="{group_url}" title="{group_name}">{group_name}</a>'
        return ''
    newsletter_group_link.short_description = _('newsletter group')
    newsletter_group_link.admin_order_field = 'newsletter_group'

    @mark_safe
    def view_on_site(self, obj):
        link_icon = static('images/icons/external_16x16.png')
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('chapters.detail', args=[obj.slug]),
            strip_tags(obj.title),
            link_icon,
        )
        return link
    view_on_site.short_description = 'view'


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Position)
admin.site.register(ChapterMembershipType, ChapterMembershipTypeAdmin)
admin.site.register(ChapterMembershipApp, ChapterMembershipAppAdmin)
admin.site.register(ChapterMembershipAppField, ChapterMembershipAppField2Admin)
admin.site.register(ChapterMembership, ChapterMembershipAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(NoticeLog, NoticeLogAdmin)
admin.site.register(NoticeDefaultLogRecord, NoticeDefaultLogRecordAdmin)

