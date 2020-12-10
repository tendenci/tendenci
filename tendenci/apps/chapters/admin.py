
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags

from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.chapters.models import Chapter, Position, Officer
from tendenci.apps.chapters.forms import ChapterAdminForm, ChapterAdminChangelistForm, UserModelChoiceField
from tendenci.apps.theme.templatetags.static import static


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
    list_display = ('view_on_site', 'edit_link', 'title', 'group', 'admin_perms', 'admin_status')
    search_fields = ('title', 'content',)
    list_editable = ('title', 'group',)
    fieldsets = (
        (None, {'fields': (
            'title',
            'slug',
            'entity',
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
        """
        update the permissions backend
        """
        print('enter save_model')
        instance = form.save(commit=False)
        update_perms_and_save(request, form, instance)  # Returns perms
        return instance

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
