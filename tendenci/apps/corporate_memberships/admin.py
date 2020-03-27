from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.shortcuts import get_object_or_404, redirect
from django.utils.safestring import mark_safe

from tendenci.apps.corporate_memberships.models import (
    CorporateMembershipType,
    CorpMembershipApp,
    CorpMembershipAppField,
    CorpMembership,
    CorpMembershipRep,
    CorpProfile,
    Notice)
from tendenci.apps.corporate_memberships.forms import (
    CorporateMembershipTypeForm,
    CorpMembershipAppForm,
    NoticeForm,
    CorpMembershipAppFieldAdminForm,
    CorpProfileAdminForm)
from tendenci.apps.perms.admin import TendenciBaseModelAdmin

from tendenci.apps.base.utils import tcurrency

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static


class CorporateMembershipTypeAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'id', 'price', 'renewal_price', 'membership_type', 'apply_cap',
                     'membership_cap', 'allow_above_cap', 'above_cap_price', 'admin_only', 'status_detail', 'position']
    list_filter = ['name', 'price', 'status_detail']
    list_editable = ['position']
    option_fields = ['position', 'status_detail']
    if get_setting('module', 'corporate_memberships', 'usefreepass'):
        option_fields.insert(0, 'number_passes')
    fieldsets = (
        (None, {'fields': ('name', 'price', 'renewal_price', 'description')}),
        (_('Membership Options'), {'fields': ('membership_type', 'apply_cap', 'membership_cap',
                                              'allow_above_cap', 'above_cap_price')}),
        (_('Other Options'), {'fields': option_fields}),
    )

    form = CorporateMembershipTypeForm
    ordering = ['-position']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
        )

    def get_queryset(self, request):
        qs = super(CorporateMembershipTypeAdmin, self).get_queryset(request)
        # filter out soft-deleted items
        return qs.filter(status=True)

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username

        # save the object
        instance.save()

        #form.save_m2m()

        return instance


class CorpMembershipAppFieldAdmin(admin.TabularInline):
    model = CorpMembershipAppField
    fields = ('label', 'field_name', 'display',
              'required', 'admin_only', 'position',
              )
#    readonly_fields = ('field_name',)
    extra = 0
    can_delete = False
    verbose_name = _('Section Break')
    ordering = ("position",)
    template = "corporate_memberships/admin/corpmembershipapp/tabular.html"


class CorpMembershipAppAdmin(admin.ModelAdmin):
    inlines = (CorpMembershipAppFieldAdmin, )
    prepopulated_fields = {'slug': ['name']}
    list_display = ('id', 'name', 'application_form_link', 'status_detail',
                    'dues_reps_group_with_link', 'member_reps_group_with_link')
    list_display_links = ('name',)
    search_fields = ('name', 'status_detail')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'authentication_method',
                           'description',
                           'confirmation_text', 'notes',
                           'corp_memb_type', 'payment_methods',
                           'include_tax', 'tax_rate',
                           'memb_app'
                           )},),
        (_('Parent Entities'), {'fields': ('parent_entities',)}),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Status', {'fields': (
            'status_detail',
        )}),
    )
    filter_vertical = ('parent_entities',)
    form = CorpMembershipAppForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/corpmembershipapp_tabular_inline_ordering.js'),
            static('js/global/tinymce.event_handlers.js'),
            static('js/tax_fields.js'),
        )
        css = {'all': [static('css/admin/dynamic-inlines-with-sort.css'),
                       static('css/corpmemberships-admin.css')], }

    def get_queryset(self, request):
        qs = super(CorpMembershipAppAdmin, self).get_queryset(request)
        # filter out soft-deleted items
        return qs.filter(status=True)

    @mark_safe
    def dues_reps_group_with_link(self, instance):
        if instance.dues_reps_group:
            return '<a href="%s">%s</a>' % (
                  reverse('group.detail',
                          args=[instance.dues_reps_group.slug]),
                instance.dues_reps_group.name)
        return ''
    dues_reps_group_with_link.short_description = _('Dues Reps Group')

    @mark_safe
    def member_reps_group_with_link(self, instance):
        if instance.member_reps_group:
            return '<a href="%s">%s</a>' % (
                  reverse('group.detail',
                          args=[instance.member_reps_group.slug]),
                instance.member_reps_group.name)
        return ''
    member_reps_group_with_link.short_description = _('Member Reps Group')


class StatusDetailFilter(SimpleListFilter):
    title = _('status detail')
    parameter_name = 'status_detail'

    def lookups(self, request, model_admin):
        status_detail_list = CorpMembership.objects.exclude(
                        status_detail='archive'
                        ).distinct('status_detail'
                        ).values_list('status_detail',
                        flat=True).order_by('status_detail')
        return [(status_detail, status_detail
                 ) for status_detail in status_detail_list]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(
                    status_detail=self.value())
        return queryset


def approve_selected(modeladmin, request, queryset):
    """
    Approves selected corp memberships.
    """
    # process only pending corp. memberships
    corp_memberships = queryset.filter(
        status=True, status_detail__in=['pending', 'paid - pending approval'])

    for corp_membership in corp_memberships:
        if corp_membership.renewal:
            corp_membership.approve_renewal(request)
        else:
            corp_membership.approve_join(request,
                                **{'create_new': True,
                              'assign_to_user': None})

approve_selected.short_description = u'Approve selected'

class CorpMembershipAdmin(TendenciBaseModelAdmin):
    list_display = ['profile',
                    'statusdetail',
                    'parent_entity',
                    'cm_type',
                    'join_date',
                    'renew_date',
                    'expire_date',
#                     'dues_reps',
#                     'member_reps',
                    'roster_link',
                    'invoice_url']
    list_filter = ['corporate_membership_type', StatusDetailFilter, 'join_dt', 'expiration_dt']
    search_fields = ['corp_profile__name']

    actions = [approve_selected,]

    fieldsets = (
        (None, {'fields': ()}),
    )

    def get_queryset(self, request):
        """
        Excludes archive
        """
        return super(CorpMembershipAdmin, self).get_queryset(request
                    ).exclude(status_detail='archive'
                              ).order_by('status_detail',
                                         'corp_profile__name')

    @mark_safe
    def profile(self, instance):
        return '<a href="%s">%s</a>' % (
              reverse('admin:corporate_memberships_corpprofile_change',
                      args=[instance.corp_profile.id]),
              instance.corp_profile.name,)
    profile.short_description = _('Corp Profile')
    profile.admin_order_field = 'corp_profile__name'

    def statusdetail(self, instance):
        return instance.status_detail
    statusdetail.short_description = _('Status')
    statusdetail.admin_order_field = 'status_detail'

    def parent_entity(self, instance):
        return instance.corp_profile.parent_entity
    parent_entity.short_description = _('Parent Entity')
    parent_entity.admin_order_field = 'corp_profile__parent_entity'

    @mark_safe
    def cm_type(self, instance):
        return '<a href="%s">%s</a>' % (
              reverse('admin:corporate_memberships_corporatemembershiptype_change',
                      args=[instance.corporate_membership_type.id]),
              instance.corporate_membership_type.name,)
    cm_type.short_description = _('Membership Type')
    cm_type.admin_order_field = 'corporate_membership_type'

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
        if not instance.expiration_dt:
            return ''
        return instance.expiration_dt.strftime('%m-%d-%Y')
    expire_date.short_description = _('Expiration Date')
    expire_date.admin_order_field = 'expiration_dt'

    @mark_safe
    def edit_link(self, instance):
        return '<a href="%s">%s</a>' % (
                    reverse('corpmembership.edit',args=[instance.id]),
                    _('Edit'),)
    edit_link.short_description = _('edit')

    @mark_safe
    def roster_link(self, instance):
        return '<a href="%s?cm_id=%d">%s</a>' % (
                    reverse('corpmembership.roster_search'),
                    instance.id,
                    _('Roster'),)
    roster_link.short_description = _('Roster')

    def display_reps(self, reps):
        reps_display = ''
        for i, rep in enumerate(reps):
            if i > 0:
                reps_display += '<br />'
            reps_display += '<a href="%s">%s</a> ' % (
                        reverse('profile',args=[rep.user.username]),
                        rep.user.get_full_name() or rep.user.username)

            if rep.user.email:
                reps_display += rep.user.email
        return reps_display

    @mark_safe
    def dues_reps(self, instance):
        reps = instance.corp_profile.reps.filter(is_dues_rep=True)
        return self.display_reps(reps)
    dues_reps.short_description = _('Dues Reps')

    @mark_safe
    def member_reps(self, instance):
        reps = instance.corp_profile.reps.filter(is_member_rep=True)
        return self.display_reps(reps)
    member_reps.short_description = _('Member Reps')

    @mark_safe
    def invoice_url(self, instance):
        invoice = instance.invoice
        if invoice:
            if invoice.balance > 0:
                return '<a href="%s">Invoice %s (%s)</a>' % (
                    invoice.get_absolute_url(),
                    invoice.pk,
                    tcurrency(invoice.balance)
                )
            else:
                return '<a href="%s">Invoice %s</a>' % (
                    invoice.get_absolute_url(),
                    invoice.pk
                )
        return ""
    invoice_url.short_description = u'Invoice'

    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(reverse('corpmembership.add'))

    def change_view(self, request, object_id, form_url='',
                    extra_context=None):
        return HttpResponseRedirect(reverse('corpmembership.view',
                                            args=[object_id]))

    def log_deletion(self, request, object, object_repr):
        description = 'Corporate membership - %s (id=%d, corp_profile_id=%d) - deleted' % (
                                            object.corp_profile.name,
                                            object.id,
                                            object.corp_profile.id)
        EventLog.objects.log(instance=object, description=description)
        super(CorpMembershipAdmin, self).log_deletion(request, object, object_repr)


class NoticeAdmin(admin.ModelAdmin):
    @mark_safe
    def notice_log(self):
        if self.notice_time == 'attimeof':
            return '--'
        return '<a href="%s%s?notice_id=%d">View logs</a>' % (get_setting('site', 'global', 'siteurl'),
                         reverse('corporate_membership.notice.log.search'), self.id)

    list_display = ['id', 'notice_name', notice_log, 'content_type',
                     'corporate_membership_type', 'status_detail']
    list_display_links  = ['notice_name']
    list_filter = ['notice_type', 'status_detail']

    fieldsets = (
        (None, {'fields': ('notice_name', 'notice_time_type', 'corporate_membership_type')}),
        (_('Email Fields'), {'fields': ('subject', 'content_type', 'sender', 'sender_display', 'email_content')}),
        (_('Other Options'), {'fields': ('status_detail',)}),
    )

    form = NoticeForm

    class Media:
        js = (
            "//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js",
            static('js/global/tinymce.event_handlers.js'),
        )

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)

        # save the expiration method fields
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

    def get_urls(self):
        urls = super(NoticeAdmin, self).get_urls()
        extra_urls = [
            url(r'^clone/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.clone),
                name='corporate_membership_notice.admin_clone'),
        ]
        return extra_urls + urls

    def clone(self, request, pk):
        """
        Make a clone of this notice.
        """
        notice = get_object_or_404(Notice, pk=pk)
        notice_clone = Notice()

        ignore_fields = ['guid', 'id', 'create_dt', 'update_dt',
                         'creator', 'creator_username',
                         'owner', 'owner_username']
        field_names = [field.name
                        for field in notice.__class__._meta.fields
                        if field.name not in ignore_fields]

        for name in field_names:
            setattr(notice_clone, name, getattr(notice, name))

        notice_clone.notice_name = 'Clone of %s' % notice_clone.notice_name
        notice_clone.creator = request.user
        notice_clone.creator_username = request.user.username
        notice_clone.owner = request.user
        notice_clone.owner_username = request.user.username
        notice_clone.save()

        return redirect(reverse(
            'admin:corporate_memberships_notice_change',
            args=[notice_clone.pk],
        ))


class AppListFilter(SimpleListFilter):
    title = _('Corp. Memb. App')
    parameter_name = 'corp_app_id'

    def lookups(self, request, model_admin):
        apps_list = CorpMembershipApp.objects.filter(
                        status=True,
                        status_detail__in=['active', 'published']
                        ).values_list('id', 'name'
                        ).order_by('id')
        return [(app_tuple[0], app_tuple[1]) for app_tuple in apps_list]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(
                    corp_app_id=int(self.value()))
        queryset = queryset.filter(display=True)
        return queryset


class CorpMembershipAppField2Admin(admin.ModelAdmin):
    model = CorpMembershipAppField
    list_display = ['label', 'app_link', 'field_name', 'display',
              'required', 'admin_only', 'position',
              ]

    readonly_fields = ('corp_app', 'field_name')

    list_editable = ['position']
    ordering = ("position",)
    list_filter = (AppListFilter,)
    form = CorpMembershipAppFieldAdminForm

    class Media:
        js = (
            "//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js",
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
        )

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
        fields = ('corp_app', 'label', 'field_name', 'field_type',
                    ('display', 'required',), 'admin_only',
                             ) + tuple(extra_fields)

        return ((None, {'fields': fields
                        }),)

    def get_object(self, request, object_id, from_field=None):
        obj = super(CorpMembershipAppField2Admin, self).get_object(request, object_id, from_field=from_field)

        # assign default field_type
        if obj:
            if not obj.field_type:
                if not obj.field_name:
                    obj.field_type = 'section_break'
                else:
                    obj.field_type = CorpMembershipAppField.get_default_field_type(obj.field_name)

        return obj

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        return None


class CorpMembershipRepInlineAdmin(admin.TabularInline):
    model = CorpMembershipRep
    fields = ('user', 'is_dues_rep', 'is_member_rep')
    extra = 0
    raw_id_fields = ("user",)
    verbose_name = _('Representative')
    verbose_name_plural = _('Representatives')
    ordering = ("user",)


class CorpMembershipInlineAdmin(admin.TabularInline):
    model = CorpMembership
    fields = ('corporate_membership_type',
              'join_dt',
              'renewal', 'renew_dt',
              'expiration_dt',
              'status_detail')
    readonly_fields=('corporate_membership_type',
                     'join_dt',
                      'renewal', 'renew_dt',
                      'expiration_dt',
                      'status_detail')
    extra = 0
    can_delete = False
    ordering = ("-create_dt", '-expiration_dt')

    def has_add_permission(self, request, obj=None):
        return False


class CorpProfileAdmin(TendenciBaseModelAdmin):
    model = CorpProfile
    list_display = ['name',]
    search_fields = ('name',)
    inlines = (CorpMembershipRepInlineAdmin, CorpMembershipInlineAdmin)
    fieldsets = [(_('Company Details'), {
                      'fields': ('name',
                                 'logo_file',
                                 'url',
                                 'number_employees',
                                 'phone',
                                 'email',
                                 'address',
                                 'address2',
                                 'city',
                                 'state',
                                 'zip',
                                 'country',
                                 'entity'),
                      }),
                      (_('Parent Entity'), {
                       'fields': ('parent_entity',),
                       'classes': ('boxy-grey',),
                      }),
                     (_('Other Info'), {'fields': (
                            'description',
                            'notes',
                        )}),]

    form = CorpProfileAdminForm

    def has_add_permission(self, request):
        return False


class CorpMembershipRepAdmin(admin.ModelAdmin):
    model = CorpMembershipRep
    list_display = ['id', 'profile', 'rep_name', 'rep_email',
                    'is_dues_rep', 'is_member_rep']
    list_filter = ['is_dues_rep', 'is_member_rep']

    ordering = ['corp_profile']

    def get_queryset(self, request):
        """
        Excludes those associated with the deleted corp profiles
        """
        return super(CorpMembershipRepAdmin, self).get_queryset(request
                    ).filter(corp_profile__status=True)
    
    @mark_safe
    def profile(self, instance):
        return '<a href="%s">%s</a>' % (
              reverse('admin:corporate_memberships_corpprofile_change',
                      args=[instance.corp_profile.id]),
              instance.corp_profile.name,)
    profile.short_description = _('Corp Profile')
    profile.admin_order_field = 'corp_profile__name'

    @mark_safe
    def rep_name(self, instance):
        return '<a href="{0}">{1}</a>'.format(
                reverse('profile', args=[instance.user.username]),
                instance.user.get_full_name() or instance.user.username,

            )
    rep_name.short_description = u'Rep Name'
    rep_name.admin_order_field = 'user__first_name'

    def rep_email(self, instance):
        return instance.user.email
    rep_email.short_description = u'Rep Email'
    rep_email.admin_order_field = 'user__email'


admin.site.register(CorpMembership, CorpMembershipAdmin)
admin.site.register(CorporateMembershipType, CorporateMembershipTypeAdmin)
admin.site.register(CorpMembershipApp, CorpMembershipAppAdmin)
admin.site.register(CorpMembershipAppField, CorpMembershipAppField2Admin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(CorpProfile, CorpProfileAdmin)
admin.site.register(CorpMembershipRep, CorpMembershipRepAdmin)
