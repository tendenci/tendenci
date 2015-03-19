from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.meta.models import Meta as MetaTags
from tendenci.apps.pages.models import Page
from tendenci.apps.pages.forms import PageAdminForm

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


class PageAdmin(admin.ModelAdmin):
    list_display = ('view_on_site', 'edit_link', 'title', 'link', 'syndicate',
                    'allow_anonymous_view','status_detail', 'group', 'tags')
    search_fields = ('title','content',)
    list_editable = ['title', 'tags', 'group']
    list_filter = ('group', )
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'group', 'tags', 'template')}),
        (_('Meta'), {'fields': (
            'meta_title',
            'meta_keywords',
            'meta_description',
            'meta_canonical_url')}),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        (_('Publishing Status'), {'fields': (
            'syndicate',
            'status_detail'
        )}),
    )
    prepopulated_fields = {'slug': ['title']}
    form = PageAdminForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def link(self, obj):
        return '<a href="%s" title="%s">%s</a>' % (
            obj.get_absolute_url(),
            obj.title,
            obj.slug
        )
    link.allow_tags = True
    link.admin_order_field = 'slug'

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:pages_page_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = _('edit')

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" alt="%s" title="%s" /></a>' % (
            reverse('page', args=[obj.slug]),
            obj.title,
            link_icon,
            obj.title,
            obj.title
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = _('view')

    def log_deletion(self, request, object, object_repr):
        super(PageAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 583000,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_change(self, request, object, message):
        super(PageAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 582000,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_addition(self, request, object):
        super(PageAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 581000,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name,
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance)

        if instance.meta:
            meta = instance.meta
        else:
            meta = MetaTags()

        meta.title = form.cleaned_data['meta_title']
        meta.description = form.cleaned_data['meta_description']
        meta.keywords = form.cleaned_data['meta_keywords']
        meta.canonical_url = form.cleaned_data['meta_canonical_url']
        meta.save()
        instance.meta = meta
        instance.save()

        # notifications
        if not request.user.profile.is_superuser:
            # send notification to administrators
            recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
            notice_type = 'page_added'
            if change: notice_type = 'page_edited'
            if recipients:
                if notification:
                    extra_context = {
                        'object': instance,
                        'request': request,
                    }
                    notification.send_emails(recipients, notice_type, extra_context)

        return instance

admin.site.register(Page, PageAdmin)
