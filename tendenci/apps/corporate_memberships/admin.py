from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.urls import path, re_path
from django.shortcuts import get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.contrib import messages

from tendenci.apps.corporate_memberships.models import (
    CorporateMembershipType,
    CorpMembershipApp,
    CorpMembershipAppField,
    CorpMembership,
    CorpMembershipRep,
    CorpProfile, CorpProduct, Branch,
    Notice)
from tendenci.apps.corporate_memberships.forms import (
    CorporateMembershipTypeForm,
    CorpMembershipAppForm,
    NoticeForm,
    CorpMembershipAppFieldAdminForm,
    CorpProfileAdminForm,
    CorpProductForm, BranchAdminForm)
from tendenci.apps.perms.admin import TendenciBaseModelAdmin

from tendenci.apps.base.utils import tcurrency

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.templatetags.static import static
from tendenci.apps.perms.utils import update_perms_and_save


class CorporateMembershipTypeAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'id', 'price', 'renewal_price', 'get_membership_type', 'apply_cap',
                     'membership_cap', 'allow_above_cap', 'above_cap_price', 'reps_groups', 'admin_only', 'status_detail', 'position']
    list_filter = ['name', 'price', 'status_detail']
    list_editable = ['position']
    option_fields = ['require_approval', 'pending_group', 'active_group', 'admin_only', 'position', 'status_detail']
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
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
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

    @mark_safe
    def get_membership_type(self, instance):
        return '<a href="%s">%s</a>' % (
              reverse('admin:memberships_membershiptype_change',
                      args=[instance.membership_type.id]),
              instance.membership_type.name,)
    get_membership_type.short_description = _('Membership Type (Individual)')
    get_membership_type.admin_order_field = 'membership_type'
    
    @mark_safe
    def reps_groups(self, instance):
        reps_groups_links = ''
        if instance.pending_group:
            reps_groups_links = '<a href="%s">%s</a>' % (
                  reverse('group.detail',
                          args=[instance.pending_group.slug]),
                          _('Pending'))
        if instance.active_group:
            if reps_groups_links:
                reps_groups_links += '<br />'
            reps_groups_links += '<a href="%s">%s</a>' % (
                  reverse('group.detail',
                          args=[instance.active_group.slug]),
                          _('Active'))
        return reps_groups_links
    reps_groups.short_description = _('Reps Groups')


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
        (_('Donation'), {'fields': ('donation_enabled', 'donation_label', 'donation_default_amount'),
                         'description': _('If donation is enabled, a field will be added to the application\
                         on renewal to allow users to select the default amount or specify an amount to donate')}),
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
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
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


def renew_selected(modeladmin, request, queryset):
    """
    Renew selected corp memberships.
    """
    corp_membs = queryset.filter(status_detail__in=['active', 'expired'])
    if corp_membs.count() > 10:
        corp_membs = corp_membs[:10]
    corp_names = []
    has_pending = False
    return_url = None

    for corp_memb in corp_membs:
        # should it check if in renewal period?
        #if copr_memb.expiration_dt:
        if (corp_memb.can_renew() or corp_memb.is_expired) and \
            not corp_memb.latest_renewed_in_pending():
            new_corp_memb = corp_memb.renew(request)
            if new_corp_memb.status_detail == 'pending':
                has_pending = True
            #copr_memb.send_notice_email(request, 'renewal')
            corp_names.append(corp_memb.corp_profile.name)

    if corp_names:
        if has_pending:
            msg_string = f'Renewal pending: {", ".join(corp_names)}. Total: {len(corp_names)}. Please make payment and mark as approved'
        else:
            msg_string = f'Successfully renewed: {", ".join(corp_names)}. Total: {len(corp_names)}'
        return_url = request.path + '?o=-1'
    else:
        msg_string = 'Nothing to renew.'
    messages.add_message(request, messages.SUCCESS, _(msg_string))

    if return_url:
        return HttpResponseRedirect(return_url)

renew_selected.short_description = 'Renew selected (select less than 10 please)'


def export_selected_invoices(modeladmin, request, queryset):
    """
    Export invoices for the selected corp memberships.
    """
    import time as ttime
    from django.http import StreamingHttpResponse
    from tendenci.apps.invoices.models import Invoice
    from tendenci.apps.invoices.utils import iter_invoices

    invoices = Invoice.objects.filter(id__in=queryset.values_list('invoice_id', flat=True))
    response = StreamingHttpResponse(
        streaming_content=(iter_invoices(invoices)),
        content_type='text/csv',)
    response['Content-Disposition'] = f'attachment;filename=invoices_export_{ttime.time()}.csv'
    return response

export_selected_invoices.short_description = 'Export selected Invoices'


def print_selected_invoices(modeladmin, request, queryset):
    """
    Print invoices for the selected corp memberships.
    """
    from tendenci.apps.invoices.models import Invoice
    from tendenci.apps.theme.shortcuts import themed_response as render_to_resp

    invoices = Invoice.objects.filter(id__in=queryset.values_list('invoice_id', flat=True))
    template_name = "invoices/print_invoices.html"

    return render_to_resp(request=request, template_name=template_name,
        context={
        'print_view': True,
        'invoices': invoices,
        'back_link': request.get_full_path()})

print_selected_invoices.short_description = 'Print selected Invoices'


class CorpMembershipAdmin(TendenciBaseModelAdmin):
    list_display = ['profile',
                    'account_id',
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
    search_fields = ['corp_profile__name', 'corp_profile__account_id']

    actions = [approve_selected,
               renew_selected,
               export_selected_invoices,
               print_selected_invoices]

    fieldsets = (
        (None, {'fields': ()}),
    )

    def get_queryset(self, request):
        """
        Excludes archive
        """
        return super(CorpMembershipAdmin, self).get_queryset(request
                    ).exclude(status_detail='archive').exclude(
                              corp_profile__status=False,
                              ).order_by('status_detail',
                                         'corp_profile__name')

    def account_id(self, instance):
        return instance.corp_profile.account_id
    account_id.short_description = _('Account ID')
    account_id.admin_order_field = 'corp_profile__account_id'

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
        if instance.corporate_membership_type:
            return '<a href="%s">%s</a>' % (
                  reverse('admin:corporate_memberships_corporatemembershiptype_change',
                          args=[instance.corporate_membership_type.id]),
                  instance.corporate_membership_type.name,)
        return ''
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
    if (get_setting('module', 'invoices', 'taxrateuseregions') \
        or get_setting('module', 'memberships', 'taxrateuseregions')):
        list_display += ['region', 'excluded_regions']
    list_display_links  = ['notice_name']
    list_filter = ['notice_type', 'status_detail']

    form = NoticeForm

    class Media:
        js = (
            "//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js",
            static('js/global/tinymce.event_handlers.js'),
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {'fields': ['notice_name', 'notice_time_type', 'corporate_membership_type',
                               'region', 'regions_to_exclude']}),
            (_('Email Fields'), {'fields': ('subject', 'content_type', 'sender', 'sender_display', 'email_content')}),
            (_('Other Options'), {'fields': ('status_detail',)}),
            )
        if not (get_setting('module', 'invoices', 'taxrateuseregions') \
                or get_setting('module', 'memberships', 'taxrateuseregions')):
            fieldsets[0][1]['fields'].remove('region')
            fieldsets[0][1]['fields'].remove('regions_to_exclude')
        return fieldsets
        

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
            re_path(r'^clone/(?P<pk>\d+)/$',
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
            "//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js",
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

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        return super(CorpMembershipAppField2Admin, self).change_view(request, object_id, form_url,
                               extra_context=dict(show_delete=False))

#     def has_delete_permission(self, request, obj=None):
#         return False

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


class ProductInline(admin.TabularInline):
    model = CorpProduct
    form = CorpProductForm
    extra = 1
    verbose_name = 'Product'
    verbose_name_plural = 'Products'


class BranchInlineAdmin(admin.StackedInline):
    model = Branch
    fields = ('name', 'address', 'city', 'state', 'zip',
              'country', 'phone', 'fax')
    extra = 1
    verbose_name = _('Branch')
    verbose_name_plural = _('Branches')
    ordering = ("name",)
    form = BranchAdminForm


class CorpProfileAdmin(TendenciBaseModelAdmin):
    model = CorpProfile
    list_display = ['name',]
    if get_setting('module', 'trainings', 'enabled'):
        list_display.append('show_transcripts')
    search_fields = ('name',)
    inlines = (CorpMembershipRepInlineAdmin, BranchInlineAdmin,
               CorpMembershipInlineAdmin)
    if get_setting('module', 'corporate_memberships', 'useproducts'):
        inlines = (ProductInline,) + inlines
    fieldsets = [(_('Company Details'), {
                      'fields': ('name',
                                 'account_id',
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

    def save_model(self, request, object, form, change):
        """
        Update the permissions backend and log the event
        """
        instance = form.save(commit=False)
        instance.owner = request.user
        update_perms_and_save(request, form, instance)
        
        form.save_logo(instance, request.user)
        return instance

    @mark_safe
    def show_transcripts(self, instance):
        if instance:
            corp_mem = instance.corp_membership
            if corp_mem and corp_mem.members_count > 0:
                url = reverse('trainings.transcripts_corp', args=[instance.id])
                return f'<a href="{url}" title="View Transcripts">View Transcripts</a>'
        return ""
    show_transcripts.short_description = 'Transcripts'


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
