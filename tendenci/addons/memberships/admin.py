import uuid
from datetime import datetime
from django.db.models import Q
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from tendenci.addons.memberships.forms import MembershipTypeForm
from tendenci.apps.user_groups.models import Group
from tendenci.core.perms.utils import update_perms_and_save
from tendenci.addons.memberships.models import (Membership, MembershipDefault,
                                                MembershipType, Notice,
                                                AppField,
                                                MembershipAppField,
                                                MembershipApp)
from tendenci.addons.memberships.forms import (MembershipDefaultForm, AppForm,
                            NoticeForm, AppFieldForm, AppEntryForm,
                            MembershipAppForm)
from tendenci.addons.memberships.utils import (get_default_membership_fields,
                                               edit_app_update_corp_fields,
                                               get_selected_demographic_field_names)
from tendenci.addons.memberships.middleware import ExceededMaxTypes
from tendenci.core.payments.models import PaymentMethod
from tendenci.core.site_settings.utils import get_setting


class MembershipAdmin(admin.ModelAdmin):

    def member_name(self):
        return '<strong><a href="%s">%s</a></strong>' % (self.get_absolute_url(), self)
    member_name.allow_tags = True
    member_name.short_description = 'Member Name'

    list_display = (member_name, 'membership_type', 'subscribe_dt', 'expire_dt', 'payment_method')
    list_filter = ('membership_type', 'subscribe_dt', 'expire_dt', 'payment_method')

    def __init__(self, *args, **kwargs):
        super(MembershipAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


def approve_selected(modeladmin, request, queryset):
    """
    Approves selected memberships.
    Exclude active, expired, and archived memberships.

    Sends email to member, member and global recipients.
    """

    qs_active = Q(status_detail='active')
    qs_expired = Q(status_detail='expired')
    qs_archived = Q(status_detail='archive')

    # exclude already approved memberships
    memberships = queryset.exclude(
        status=True,
        application_approved_dt__isnull=False,
    ).exclude(qs_active | qs_expired | qs_archived)

    for membership in memberships:
        membership.approve(request_user=request.user)
        membership.send_email(request, 'approve')

approve_selected.short_description = u'Approve selected'


def renew_selected(modeladmin, request, queryset):
    """
    Renew selected memberships.
    Exclude archived memberships
    """

    qs_archived = Q(status_detail='archive')

    memberships = queryset.exclude(qs_archived)

    for membership in memberships:
        membership.renew(request_user=request.user)
        membership.send_email(request, 'renewal')

renew_selected.short_description = u'Renew selected'


def disapprove_selected(modeladmin, request, queryset):
    """
    Disapprove [only pending and active]
    selected memberships.
    """

    qs_pending = Q(status_detail='pending')
    qs_active = Q(status_detail='active')

    memberships = queryset.filter(qs_pending, qs_active)

    for membership in memberships:
        membership.disapprove(request_user=request.user)
        membership.send_email(request, 'disapprove')

disapprove_selected.short_description = u'Disapprove selected'


def expire_selected(modeladmin, request, queryset):
    """
    Expire [only active] selected memberships.
    """

    memberships = queryset.filter(
        status=True,
        status_detail='active',
        application_approved=True,
    )

    for membership in memberships:
        # check expire_dt + grace_period_dt
        if not membership.is_expired():
            membership.expire(request_user=request.user)

expire_selected.short_description = u'Expire selected'


class MembershipDefaultAdmin(admin.ModelAdmin):
    """
    MembershipDefault model
    """

    form = MembershipDefaultForm

    profile = ('Profile',
        {'fields': (
            ('first_name', 'last_name'),
            ('email', 'email2'),
            ('company', 'department', 'position_title'),
            ('address', 'address2', 'address_type'),
            ('city', 'state', 'zipcode', 'country'),
            ('phone', 'phone2'),
            ('work_phone', 'home_phone', 'mobile_phone'),
            ('fax'),
            ('url', 'url2'),
            ('dob', 'sex', 'spouse'),
            ('hide_in_search', 'hide_address', 'hide_email', 'hide_phone'),
        )}
    )

    membership = ('Membership',
        {'fields': (
            'member_number',
            'renewal',
            'certifications',
            'work_experience',
            'referral_source',
            'referral_source_other',
            'referral_source_member_name',
            'referral_source_member_number',
            'affiliation_member_number',
            'primary_practice',
            'how_long_in_practice',
            'notes',
            'admin_notes',
            'newsletter_type',
            'directory_type',
            'chapter',
            'areas_of_expertise',
            'corporate_membership_id',
            'home_state',
            'year_left_native_country',
            'network_sectors',
            'networking',
            'government_worker',
            'government_agency',
            'license_number',
            'license_state',
            'region',
            'industry',
            'company_size',
            'promotion_code',
            # 'directory',
            # 'sig_user_group_ids',
        )}
    )

    money = ('Money',
        {'fields': (
            'payment_method',
            'membership_type',
        )}
    )

    extra = ('Extra',
        {'fields': (
            'industry',
            'region',
        )}
    )

    status = ('Status',
        {'fields': (
            'join_dt',
            'renew_dt',
            'expire_dt',
        )}
    )

    fieldsets = (
            profile,
            membership,
            money,
            status
    )

    def get_fieldsets(self, request, instance=None):
        demographics_fields = get_selected_demographic_field_names()

        if demographics_fields:
            demographics = (
                    'Demographics',
                    {'fields': tuple(demographics_fields)
                     }
                           )
        fieldsets = (
                self.profile,
                self.membership,)
        if demographics_fields:
            fieldsets += (
                demographics,
            )
        fieldsets += (
                self.money,
                self.status)

        return fieldsets

    def name(self, instance):
        name = '%s %s' % (
            instance.user.first_name,
            instance.user.last_name,
        )
        name.strip()
        return name

    def email(self, instance):
        return instance.user.email

    def get_status(self, instance):
        return instance.get_status().capitalize()
    get_status.short_description = u'Status'

    def get_create_dt(self, instance):
        return instance.create_dt.strftime('%b %d, %Y, %I:%M %p')
    get_create_dt.short_description = u'Created On'

    def get_approve_dt(self, instance):
        dt = instance.application_approved_dt

        if dt:
            return dt.strftime('%b %d, %Y, %I:%M %p')
        return u''
    get_approve_dt.short_description = u'Approved On'

    def get_actions(self, request):
        actions = super(MembershipDefaultAdmin, self).get_actions(request)
        actions['delete_selected'][0].short_description = "Delete Selected"
        return actions

    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'member_number',
    ]

    list_display = [
        'name',
        'email',
        'member_number',
        'membership_type',
        'get_approve_dt',
        'get_status',
    ]

    list_filter = [
        'membership_type',
        'status_detail'
    ]

    actions = [
        approve_selected,
        renew_selected,
        disapprove_selected,
        expire_selected,
    ]

    def save_form(self, request, form, change):
        """
        Save membership [+ more] model
        """
        return form.save(request=request, commit=False)

    def add_view(self, request, form_url='', extra_context=None):
        """
        Intercept add page and redirect to form.
        """
        return HttpResponseRedirect(
            reverse('membership_default.add')
        )

    def queryset(self, request):
        qs = super(MembershipDefaultAdmin, self).queryset(request)
        return qs.order_by('-application_approved_dt')

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(MembershipDefaultAdmin, self).get_urls()

        extra_urls = patterns('',
            url("^approve/(?P<pk>\d+)/$",
                self.admin_site.admin_view(self.approve),
                name='membership.admin_approve'),
            url("^renew/(?P<pk>\d+)/$",
                self.admin_site.admin_view(self.renew),
                name='membership.admin_renew'),
            url("^disapprove/(?P<pk>\d+)/$",
                self.admin_site.admin_view(self.disapprove),
                name='membership.admin_disapprove'),
            url("^expire/(?P<pk>\d+)/$",
                self.admin_site.admin_view(self.expire),
                name='membership.admin_expire'),
        )
        return extra_urls + urls

    # django-admin custom views ----------------------------------------

    def approve(self, request, pk):
        """
        Approve membership and redirect to
        membershipdefault change page.
        """
        m = get_object_or_404(MembershipDefault, pk=pk)
        m.approve(request_user=request.user)
        m.send_email(request, 'approve')

        return redirect(reverse(
            'admin:memberships_membershipdefault_change',
            args=[pk],
        ))

    def renew(self, request, pk):
        """
        Renew membership and redirect to
        membershipdefault change page.
        """
        m = get_object_or_404(MembershipDefault, pk=pk)
        m.renew(request_user=request.user)
        m.send_email(request, 'renewal')

        return redirect(reverse(
            'admin:memberships_membershipdefault_change',
            args=[pk],
        ))

    def disapprove(self, request, pk):
        """
        Disapprove membership and redirect to
        membershipdefault change page.
        """
        m = get_object_or_404(MembershipDefault, pk=pk)
        m.disapprove(request_user=request.user)
        m.send_email(request, 'disapprove')

        return redirect(reverse(
            'admin:memberships_membershipdefault_change',
            args=[pk],
        ))

    def expire(self, request, pk):
        """
        Expire membership and redirect to
        membershipdefault change page.
        """
        m = get_object_or_404(MembershipDefault, pk=pk)
        m.expire(request_user=request.user)

        return redirect(reverse(
            'admin:memberships_membershipdefault_change',
            args=[pk],
        ))


class MembershipAppFieldAdmin(admin.TabularInline):
    model = MembershipAppField
    fields = ('label', 'field_name', 'display',
              'required', 'admin_only', 'order',
              )
#    readonly_fields = ('field_name',)
    extra = 0
    can_delete = False
    verbose_name = 'Section Break'
    ordering = ("order",)
    template = "memberships/admin/membershipapp/tabular.html"


class MembershipAppAdmin(admin.ModelAdmin):
    inlines = (MembershipAppFieldAdmin, )
    prepopulated_fields = {'slug': ['name']}
    list_display = ('name', 'status', 'status_detail')
    search_fields = ('name', 'status', 'status_detail')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description',
                           'confirmation_text', 'notes',
                           'membership_types', 'payment_methods',
                           'use_for_corp', 'use_captcha',)},),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Status', {'fields': (
            'status',
            'status_detail',
        )}),
#        ('Add fields to your form', {'fields': ('app_field_selection',),
#                                     'classes': ('mapped-fields', ),
#                                     'description': 'The fields you ' + \
#                                     'selected will be automatically ' + \
#                                     'added to your form.'}),
    )

    form = MembershipAppForm
    change_form_template = "memberships/admin/membershipapp/change_form.html"

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/membapp_tabular_inline_ordering.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL,
                       '%scss/memberships-admin.css' % settings.STATIC_URL], }


class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'admin_fee', 'group', 'require_approval',
                     'allow_renewal', 'renewal_price', 'renewal',
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price', 'status_detail']

    exclude = ('status',)

    fieldsets = (
        (None, {'fields': ('name', 'price', 'admin_fee', 'description')}),
        ('Expiration Method', {'fields': ('never_expires', 'type_exp_method',)}),
        ('Renewal Options', {'fields': (('allow_renewal','renewal', 'renewal_require_approval'),
                                        'renewal_price', 
                                        'renewal_period_start', 
                                        'renewal_period_end',)}),

        ('Other Options', {'fields': (
            'expiration_grace_period', ('require_approval', 
            'admin_only'), 'position', 'status_detail')}),
    )

    form = MembershipTypeForm
    ordering = ['position',]
    
    def add_view(self, request):
        num_types = MembershipType.objects.all().count()
        max_types = settings.MAX_MEMBERSHIP_TYPES
        if num_types >= max_types:
            raise ExceededMaxTypes
        return super(MembershipTypeAdmin, self).add_view(request)
    
    class Media:
        js = ("%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL, 
              "%sjs/membtype.js" % settings.STATIC_URL,)
            
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        # save the expiration method fields
        type_exp_method = form.cleaned_data['type_exp_method']
        type_exp_method_list = type_exp_method.split(",")
        for i, field in enumerate(form.type_exp_method_fields):
            if field=='fixed_option2_can_rollover':
                if type_exp_method_list[i]=='':
                    type_exp_method_list[i] = ''
            else:
                if type_exp_method_list[i]=='':
                    type_exp_method_list[i] = "0"

            setattr(instance, field, type_exp_method_list[i])
         
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            
            # create a group for this type
            group = Group()
            group.name = 'Membership: %s' % instance.name
            group.slug = slugify(group.name)
            # just in case, check if this slug already exists in group. 
            # if it does, make a unique slug
            tmp_groups = Group.objects.filter(slug__istartswith=group.slug)
            if tmp_groups:
                t_list = [g.slug[len(group.slug):] for g in tmp_groups]
                num = 1
                while str(num) in t_list:
                    num += 1
                group.slug = '%s%s' % (group.slug, str(num))
                # group name is also a unique field
                group.name = '%s%s' % (group.name, str(num))
            
            group.label = instance.name
            group.type = 'membership'
            group.email_recipient = request.user.email
            group.show_as_option = 0
            group.allow_self_add = 0
            group.allow_self_remove = 0
            group.description = "Auto-generated with the membership type. Used for membership only"
            group.notes = "Auto-generated with the membership type. Used for membership only"
            #group.use_for_membership = 1
            group.creator = request.user
            group.creator_username = request.user.username
            group.owner = request.user
            group.owner_username = request.user.username

            group.save()
            
            instance.group = group
 
        # save the object
        instance.save()
        
        #form.save_m2m()

        return instance

class NoticeAdmin(admin.ModelAdmin):
    def notice_log(self):
        if self.notice_time == 'attimeof':
            return '--'
        return '<a href="%s%s?notice_id=%d">View logs</a>' % (get_setting('site', 'global', 'siteurl'),
                         reverse('membership.notice.log.search'), self.id)
    notice_log.allow_tags = True

    list_display = ['notice_name', notice_log, 'content_type',
                     'membership_type', 'status', 'status_detail']
    list_filter = ['notice_type', 'status_detail']

    fieldsets = (
        (None, {'fields': ('notice_name', 'notice_time_type', 'membership_type')}),
        ('Email Fields', {'fields': ('subject', 'content_type', 'sender', 'sender_display', 'email_content')}),
        ('Other Options', {'fields': ('status', 'status_detail')}),
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


class AppFieldAdmin(admin.StackedInline):
    fieldsets = (
        (None, {'fields': (
            ('label','field_type', ),
            ('field_function', 'function_params'),
            (
                'required',
                'unique',
                'admin_only',
                'exportable'
            ),
            'choices',
            'help_text',
            'default_value',
            'css_class',
            'position'
        )},),
    )
    model = AppField
    form = AppFieldForm
    extra = 0
    template = "memberships/admin/stacked.html"

class AppAdmin(admin.ModelAdmin):

    def application_form_link(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), self.slug)
    application_form_link.allow_tags = True

    list_display = ('name', application_form_link)

    fieldsets = (
        (None, {'fields': ('name','slug', 'description', 'confirmation_text', 'notes', 
                           'membership_types', 'payment_methods', 'use_for_corp', 'use_captcha')},),
        ('Administrative', {'fields': ('allow_anonymous_view','user_perms', 'member_perms', 'group_perms',
                                       'status_detail')}),
    )

    class Media:
        js = (
            '%sjs/jquery-1.4.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery_ui_all_custom/jquery-ui-1.8.5.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/dynamic-inlines-with-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        css = {'all': ['%scss/admin/dynamic-inlines-with-sort.css' % settings.STATIC_URL], }


    def export_as_json(model_admin, request, queryset):
        from django.core import serializers
        from django.http import HttpResponse

        response = HttpResponse(mimetype="text/javascript")
        serializers.serialize('json', queryset, stream=response, indent=4)

        return response

    inlines = (AppFieldAdmin,)
    prepopulated_fields = {'slug': ('name',)}
    form = AppForm
    add_form_template = "memberships/admin/add_form.html"
    actions = [export_as_json]

    def add_view(self, request, form_url='', extra_context=None):
        self.inline_instances = [] # clear inline instances
        return super(AppAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [AppFieldAdmin]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        if not extra_context:
            extra_context = {}
        extra_context.update({
             'excluded_fields': ['field_type', 'no_duplicates', 'admin_only'],
             'excluded_lines': [2, 3],
         })
        extra_context.update(extra_context)

        return super(AppAdmin, self).change_view(request, object_id,
                                                 form_url=form_url,
                                                 extra_context=extra_context)
    
    def response_change(self, request, obj, *args, **kwargs):
        if request.POST.has_key('_popup'):
            return HttpResponse("""
                    <script type="text/javascript">
                        opener.dismissAddAnotherPopup(window, "%s", "%s");
                    </script>
            """ % (escape(obj._get_pk_val()), escape(obj)))
        else:
            return  super(AppAdmin, self).response_change(request, obj, *args, **kwargs)


    def get_fieldsets(self, request, instance=None):

        field_list = [
            
                    (None, {
                        'fields': ('name','slug', 'use_for_corp', 'description', 'confirmation_text', 'notes', 
                                   'membership_types', 'payment_methods', 'use_captcha'),
                    }),

                    ('Administrative', {
                        'fields': ('allow_anonymous_view','user_perms', 'member_perms', 'group_perms','status_detail'),
                    }),

                    ('Form Fields', {
                        'fields': [],
                        'description': 'You will have the chance to add or manage the form fields after saving.'
                    }),
        ]

        if instance: # editing
            field_list.pop() # removes default message (last item)

        return field_list

    def save_model(self, request, object, form, change):
        app = form.save(commit=False)
        add = not change

        # update all permissions and save the model
        app = update_perms_and_save(request, form, app)

        if add:
            # default application fields
            for default_field in get_default_membership_fields(use_for_corp=app.use_for_corp):
                default_field.update({'app':app})
                AppField.objects.create(**default_field)
                
        if change:
            edit_app_update_corp_fields(app)

        form.save_m2m()

        reserved_names = (
            'membership_type',
            'payment_method',
            'first_name',
            'last_name',
            'email',
            'corporate_membership'
        )

        for field in app.fields.visible():

            if 'membership-type' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(MembershipType)
                choices = [item.name for item in app.membership_types.all()]
                field.choices = ", ".join(choices)
            elif 'payment-method' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(PaymentMethod)
                choices = [item.human_name for item in app.payment_methods.all()]
                field.choices = ", ".join(choices)
            if 'first-name' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(User)
            elif 'last-name' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(User)
            elif 'email' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(User)
            elif 'corporate_membership_id' in field.field_type:
                field.content_type = ContentType.objects.get_for_model(Membership)

            if not field.field_name in reserved_names:
                field.field_name = slugify(field.label).replace('-', '_')

                # check field_name after slugify
                if field.field_name in reserved_names:
                    hex_tail = uuid.uuid1().get_hex()[:3]
                    field.field_name = '%s_%s' % (field.field_name, hex_tail)

            field.save()

        return app


class AppEntryAdmin(admin.ModelAdmin):
    form = AppEntryForm
    actions = ['disapprove']

    def disapprove(self, request, entries):
        for entry in entries:
            entry.is_approved = False
            entry.decision_dt = datetime.now()
            entry.judge = request.user
            entry.save()

    def get_actions(self, request):
        actions = super(AppEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def entry_name(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), self)
    entry_name.allow_tags = True
    entry_name.short_description = 'Submission'

    list_display = (entry_name, 'is_approved',)
    list_filter = ('app', 'is_approved')

    def __init__(self, *args, **kwargs):
        super(AppEntryAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


admin.site.register(MembershipDefault, MembershipDefaultAdmin)
admin.site.register(MembershipApp, MembershipAppAdmin)
admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(Notice, NoticeAdmin)
#admin.site.register(App, AppAdmin)
