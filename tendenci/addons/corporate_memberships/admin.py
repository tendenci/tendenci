from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.admin import SimpleListFilter
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404, redirect

from tendenci.addons.corporate_memberships.models import (
    CorporateMembershipType,
    CorpMembershipApp,
    CorpMembershipAppField,
    CorpMembership,
    CorporateMembership,
    Notice)
from tendenci.addons.corporate_memberships.models import CorpApp, CorpField
from tendenci.addons.corporate_memberships.forms import (
    CorporateMembershipTypeForm,
    CorpMembershipAppForm,
    CorpFieldForm,
    CorpAppForm,
    NoticeForm,
    CorpMembershipAppFieldAdminForm)

from tendenci.addons.corporate_memberships.utils import (
    get_corpapp_default_fields_list,
    update_authenticate_fields,
    edit_corpapp_update_memb_app)

from tendenci.core.base.utils import tcurrency

from tendenci.core.event_logs.models import EventLog
from tendenci.core.site_settings.utils import get_setting


class CorporateMembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'renewal_price', 'membership_type',
                     'admin_only', 'status_detail', 'position']
    list_filter = ['name', 'price', 'status_detail']
    list_editable = ['position']
    option_fields = ['position', 'status_detail']
    if get_setting('module', 'corporate_memberships', 'usefreepass'):
        option_fields.insert(0, 'number_passes')
    fieldsets = (
        (None, {'fields': ('name', 'price', 'renewal_price',
                           'membership_type', 'description')}),
        ('Individual Pricing Options', {'fields':
                                    ('apply_threshold', 'individual_threshold',
                                    'individual_threshold_price',)}),
        ('Other Options', {'fields': option_fields}),
    )

    form = CorporateMembershipTypeForm

    class Media:
        js = (
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.17.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )

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
    verbose_name = 'Section Break'
    ordering = ("position",)
    template = "corporate_memberships/admin/corpmembershipapp/tabular.html"


class CorpMembershipAppAdmin(admin.ModelAdmin):
    inlines = (CorpMembershipAppFieldAdmin, )
    prepopulated_fields = {'slug': ['name']}
    list_display = ('name', 'application_form_link', 'status_detail')
    search_fields = ('name', 'status_detail')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'authentication_method',
                           'description',
                           'confirmation_text', 'notes',
                           'corp_memb_type', 'payment_methods',
                           'memb_app'
                           )},),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Status', {'fields': (
            'status_detail',
        )}),
    )

    form = CorpMembershipAppForm

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/corpmembershipapp_tabular_inline_ordering.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL,
                       '%scss/corpmemberships-admin.css' % settings.STATIC_URL], }


#class FieldInline(admin.TabularInline):
class FieldInline(admin.StackedInline):
    model = CorpField
    extra = 0
    form = CorpFieldForm
    fieldsets = (
        (None, {'fields': (('label', 'field_type'),
        ('choices', 'field_layout'), 'size', ('required', 'visible', 'no_duplicates', 'admin_only'), 
            'instruction', 'default_value', 'css_class', 'position')}),
    )
    #raw_id_fields = ("page", 'section', 'field') 
    template = "corporate_memberships/admin/stacked.html"
  
class CorpAppAdmin(admin.ModelAdmin):
    def corp_app_form_link(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), self.slug)
    corp_app_form_link.allow_tags = True
    
    list_display = ['name', corp_app_form_link, 'status_detail']
    list_filter = ['name', 'status_detail']
    
    #fieldsets = (
    #    (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 'notes')}),
    #    ('Other Options', {'fields': (
    #        ('use_captcha', 'require_login'), 'status_detail')}),
    #)
    
    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/dynamic-inlines-with-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            #'%sjs/admin/corpapp.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/corpapp-inline.css' % settings.STATIC_URL], }
        
    inlines = [FieldInline]
    prepopulated_fields = {'slug': ('name',)}
    form = CorpAppForm
    add_form_template = "corporate_memberships/admin/add_form.html"
    
    #radio_fields = {"corp_memb_type": admin.VERTICAL}
    
    def add_view(self, request, form_url='', extra_context=None):
        self.inline_instances = []
        return super(CorpAppAdmin, self).add_view(request, form_url,
                                              extra_context) 
    
    def change_view(self, request, object_id, form_url='',  extra_context=None):
        self.inlines = [FieldInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        # exclude fields for corporate_membership_type and payment_method
        excluded_lines = [2, 3]  # exclude lines in inline field_set - 'choices', 'field_layout', 'size' 
        excluded_fields = ['field_type', 'no_duplicates', 'admin_only']
        fields_to_check = ['corporate_membership_type', 'payment_method']
        if extra_context:
            extra_context.update({
                                  'excluded_lines': excluded_lines,
                                  "excluded_fields":excluded_fields,
                                  'fields_to_check': fields_to_check
                                  })
        else:
            extra_context = {'excluded_lines': excluded_lines,
                             "excluded_fields":excluded_fields,
                             'fields_to_check': fields_to_check}
            
        return  super(CorpAppAdmin, self).change_view(request, object_id, form_url=form_url,
                                              extra_context=extra_context)
        

    def get_fieldsets(self, request, obj=None):
        if obj and obj.id:
            return  (
                        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 
                                           'memb_app', 'payment_methods', 'description', 
                                           'confirmation_text', 'notes')}),
                        ('Other Options', {'fields': (
                            'status_detail',)}),
                    ) 
        else:
            return (
                        (None, {'fields': ('name', 'slug', 'corp_memb_type', 'authentication_method', 
                                           'memb_app', 'payment_methods', 'description', 
                                           'confirmation_text', 'notes')}),
                        ('Other Options', {'fields': (
                             'status_detail',)}),
                        ('Form Fields', {'fields':(), 
                                         'description': 'You will have the chance to add or manage the form fields later on editing.'}),
                    )

    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        set_default_fields = False
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            set_default_fields = True
 
        # save the object
        instance.save()
        
        if set_default_fields:
            # set some default fields to the app
            fields_list = get_corpapp_default_fields_list()
            if fields_list:
                for field_d in fields_list:
                    field_d.update({'corp_app':instance})
                    f = CorpField(**field_d)
                    f.save()
                                    
        form.save_m2m()
        
        if change and instance.authentication_method == 'secret_code':
            # check for existing corporate memberships for secret code,
            # assign secret code if not assigned already
            corp_membs = CorporateMembership.objects.filter(corp_app=instance)
            if corp_membs:
                for corp_memb in corp_membs:
                    if not corp_memb.secret_code:
                        corp_memb.assign_secret_code()
                        corp_memb.save()
        
        return instance
    
    def log_deletion(self, request, object, object_repr):
        source = inspect.getmodule(self).__name__
        EventLog.objects.log(instance=object, event_type="delete", source=source)
        super(CorpAppAdmin, self).log_deletion(request, object, object_repr)


    def log_change(self, request, object, message):
        update_authenticate_fields(object)
        edit_corpapp_update_memb_app(object)
        super(CorpAppAdmin, self).log_change(request, object, message)


    def log_addition(self, request, object):
        update_authenticate_fields(object)
        edit_corpapp_update_memb_app(object)
        super(CorpAppAdmin, self).log_addition(request, object)


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


class CorpMembershipAdmin(admin.ModelAdmin):
    list_display = ['corp_profile',
                    'expiration_dt',
                    'approved', 'status_detail',
                    'invoice_url']
    list_filter = [StatusDetailFilter, 'join_dt', 'expiration_dt']
    search_fields = ['corp_profile__name']

    fieldsets = (
        (None, {'fields': ()}),
    )

    def queryset(self, request):
        return super(CorpMembershipAdmin, self).queryset(request
                    ).exclude(status_detail='archive'
                              ).order_by('status_detail',
                                         'corp_profile__name')
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
    invoice_url.allow_tags = True

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
    def notice_log(self):
        if self.notice_time == 'attimeof':
            return '--'
        return '<a href="%s%s?notice_id=%d">View logs</a>' % (get_setting('site', 'global', 'siteurl'),
                         reverse('corporate_membership.notice.log.search'), self.id)
    notice_log.allow_tags = True

    list_display = ['notice_name', notice_log, 'content_type',
                     'corporate_membership_type', 'status_detail']
    list_filter = ['notice_type', 'status_detail']

    fieldsets = (
        (None, {'fields': ('notice_name', 'notice_time_type', 'corporate_membership_type')}),
        ('Email Fields', {'fields': ('subject', 'content_type', 'sender', 'sender_display', 'email_content')}),
        ('Other Options', {'fields': ('status_detail',)}),
    )

    form = NoticeForm

    class Media:
        js = (
            "%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
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
        extra_urls = patterns('',
            url("^clone/(?P<pk>\d+)/$",
                self.admin_site.admin_view(self.clone),
                name='corporate_membership_notice.admin_clone'),
        )
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
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            'js/jquery-ui-1.8.17.custom.min.js',
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
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
                    ('display', 'required', 'admin_only'),
                             ) + tuple(extra_fields)

        return ((None, {'fields': fields
                        }),)

    def get_object(self, request, object_id):
        obj = super(CorpMembershipAppField2Admin, self).get_object(request, object_id)

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

    def response_change(self, request, obj):
        """
        If the 'Save' button is clicked, redirect to fields list
        with the selected app.
        """
        if "_save" in request.POST:
            opts = obj._meta
            verbose_name = opts.verbose_name
            module_name = opts.module_name
            if obj._deferred:
                opts_ = opts.proxy_for_model._meta
                verbose_name = opts_.verbose_name
                module_name = opts_.module_name

            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {
                        'name': force_unicode(verbose_name),
                        'obj': force_unicode(obj)}
            self.message_user(request, msg)
            post_url = '%s?corp_app_id=%d' % (
                            reverse('admin:%s_%s_changelist' %
                                   (opts.app_label, module_name),
                                   current_app=self.admin_site.name),
                            obj.corp_app_id)
            return HttpResponseRedirect(post_url)
        else:
            return super(CorpMembershipAppField2Admin, self).response_change(request, obj)

admin.site.register(CorpMembership, CorpMembershipAdmin)
admin.site.register(CorporateMembershipType, CorporateMembershipTypeAdmin)
admin.site.register(CorpMembershipApp, CorpMembershipAppAdmin)
admin.site.register(CorpMembershipAppField, CorpMembershipAppField2Admin)
admin.site.register(Notice, NoticeAdmin)
