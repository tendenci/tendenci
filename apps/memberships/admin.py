import uuid
from datetime import datetime
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.utils.html import escape
from django.core.urlresolvers import reverse

from memberships.forms import MembershipTypeForm
from user_groups.models import Group
from event_logs.models import EventLog
from perms.utils import update_perms_and_save 
from memberships.models import  Membership, MembershipType, Notice, App, AppField, AppEntry
from memberships.forms import AppForm, NoticeForm, AppFieldForm, AppEntryForm
from memberships.utils import get_default_membership_fields, edit_app_update_corp_fields
from payments.models import PaymentMethod
from site_settings.utils import get_setting


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

class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'admin_fee', 'group', 'require_approval',
                     'allow_renewal', 'renewal_price', 'renewal',  
                     'admin_only', 'status_detail']
    list_filter = ['name', 'price', 'status_detail']
    
    fieldsets = (
        (None, {'fields': ('name', 'price', 'admin_fee', 'description')}),
        ('Expiration Method', {'fields': ('never_expires', 'type_exp_method',)}),
        ('Renewal Options', {'fields': (('allow_renewal','renewal', 'renewal_require_approval'), 
                                        'renewal_price', 
                                        'renewal_period_start', 
                                        'renewal_period_end',)}),

        ('Other Options', {'fields': (
            'expiration_grace_period', ('require_approval', 
            'admin_only'), 'order', 'status', 'status_detail')}),
    )

    form = MembershipTypeForm
    
    class Media:
        js = ("%sjs/jquery-1.4.2.min.js" % settings.STATIC_URL, 
              "%sjs/membtype.js" % settings.STATIC_URL,)
        
    def log_deletion(self, request, object, object_repr):
        super(MembershipTypeAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 475300,
            'event_data': '%s %s(%d) deleted by %s' % (object._meta.object_name, 
                                                    object.name, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(MembershipTypeAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 475200,
            'event_data': '%s %s(%d) edited by %s' % (object._meta.object_name, 
                                                    object.name, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(MembershipTypeAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 475100,
            'event_data': '%s %s(%d) added by %s' % (object._meta.object_name, 
                                                   object.name, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
        
    
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
        
    def log_deletion(self, request, object, object_repr):
        super(NoticeAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 903000,
            'event_data': '%s %s(%d) deleted by %s' % (object._meta.object_name, 
                                                    object.notice_name, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(NoticeAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 902000,
            'event_data': '%s %s(%d) edited by %s' % (object._meta.object_name, 
                                                    object.notice_name, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(NoticeAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 901000,
            'event_data': '%s %s(%d) added by %s' % (object._meta.object_name, 
                                                   object.notice_name, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
        
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
                                       'status','status_detail')}),
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

    def log_deletion(self, request, object, object_repr):
        super(AppAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 653000,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(AppAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 652000,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(AppAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 651000,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)


    def add_view(self, request, form_url='', extra_context=None):
        self.inline_instances = [] # clear inline instances
        return super(AppAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, extra_context={}):

        self.inlines = [AppFieldAdmin]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)

        extra_context.update({
            'excluded_fields':['field_type', 'no_duplicates', 'admin_only'],
            'excluded_lines':[2, 3],
        })
        extra_context.update(extra_context)

        return super(AppAdmin, self).change_view(request, object_id, extra_context)
    
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
                        'fields': ('allow_anonymous_view','user_perms', 'member_perms', 'group_perms','status','status_detail'),
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
                field.field_name = slugify(field.label).replace('-','_')

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


# these get auto-created when the application gets filled out
# admin.site.register(Membership, MembershipAdmin)

admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(App, AppAdmin)
# admin.site.register(AppEntry, AppEntryAdmin)










