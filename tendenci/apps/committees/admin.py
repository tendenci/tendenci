from __future__ import print_function
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.user_groups.models import GroupMembership
from tendenci.apps.committees.models import Committee, Position, Officer
from tendenci.apps.committees.forms import CommitteeAdminForm, CommitteeAdminChangelistForm, UserModelChoiceField


class OfficerAdminInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': (
            'position',
            'user',
            'phone',
        )},),
    )
    extra = 0
    model = Officer

    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'user':

            group_members = []
            committee = None
            committee = self.get_object(kwargs['request'], Committee)
            if committee:
                committee_group = committee.group
                return UserModelChoiceField(queryset=User.objects.filter(group_member__group=committee.group), label="User")
            return UserModelChoiceField(queryset=User.objects.none(), label="User")
        return super(OfficerAdminInline, self).formfield_for_dbfield(field, **kwargs)

    def get_object(self, request, model):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
        try:
            object_id = int(object_id)
        except ValueError:
            return None
        return model.objects.get(pk=object_id)


class CommitteeAdmin(TendenciBaseModelAdmin):
    list_display = ('view_on_site', 'edit_link', 'title', 'group', 'admin_perms', 'admin_status')
    search_fields = ('title', 'content',)
    list_editable = ('title', 'group',)
    fieldsets = (
        (None, {'fields': (
            'title',
            'slug',
            'group',
            'mission',
            'content',
            'notes',
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
    form = CommitteeAdminForm
    inlines = (OfficerAdminInline,)

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(CommitteeAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_changelist_form(self, request, **kwargs):
        """
        Returns a Form class for use in the Formset on the changelist page.
        We return our custom form to filter out inactive groups.
        """
        return CommitteeAdminChangelistForm

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        print('enter save_model')
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def save_formset(self, request, form, formset, change):
        """
        Associate the user to each instance saved.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            instance.content_type = ContentType.objects.get_for_model(instance.committee)
            instance.object_id = instance.committee.pk
            instance.creator = request.user
            instance.owner = request.user
            instance.save()

    def link(self, obj):
        return '<a href="%s" title="%s">%s</a>' % (
            obj.get_absolute_url(),
            obj.title,
            obj.slug
        )
    link.allow_tags = True

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:committees_committee_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('committees.detail', args=[obj.slug]),
            obj.title,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'


admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Position)
