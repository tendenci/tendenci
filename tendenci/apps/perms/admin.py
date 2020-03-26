from operator import or_
from functools import reduce

from django.contrib import admin
from django.contrib.admin import SimpleListFilter, helpers
from django.contrib.admin.utils import get_deleted_objects, model_ngettext
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import iri_to_uri, force_text
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.db import router
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe

from tagging.models import TaggedItem
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.theme.templatetags.static import static


class TendenciBaseModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin class to help with event logs
    """

    class Media:
        js = (static('js/global/tinymce.event_handlers.js'),)

    def __init__(self, *args, **kwargs):
        super(TendenciBaseModelAdmin, self).__init__(*args, **kwargs)

        # Update the list_display to add view_on_site and edit_link if they
        # are not already added. - JMO 2012-05-15
        self.list_display = list(self.list_display)
        if 'action_checkbox' in self.list_display:
            index = self.list_display.index('action_checkbox')
            self.list_display.pop(index)

        if hasattr(self.model, "get_absolute_url"):
            if 'view_on_site' not in self.list_display:
                self.list_display.insert(0, 'view_on_site')

        if 'edit_link' not in self.list_display:
            self.list_display.insert(0, 'edit_link')

        if 'id' not in self.list_display:
            self.list_display.insert(0, 'id')

        self.list_display_links = ('edit_link', )

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = _('edit')

    @mark_safe
    def view_on_site(self, obj):
        if not hasattr(obj, 'get_absolute_url'):
            return None

        link_icon = static('images/icons/external_16x16.png')
        link = '<a href="%s" title="%s"><img src="%s" alt="external_16x16" title="external icon"/></a>' % (
            obj.get_absolute_url(),
            obj,
            link_icon,
        )
        return link
    view_on_site.short_description = _('view')

    @mark_safe
    def owner_link(self, obj):
        link = ''
        if obj.owner_username:
            link = '<a href="%s" title="%s">%s</a>' % (
                reverse('profile', args=[obj.owner_username]),
                obj.owner_username,
                obj.owner_username,
            )
        return link
    owner_link.short_description = _('owner')

    @mark_safe
    def admin_status(self, obj):
        return obj.obj_status
    admin_status.short_description = _('status')

    @mark_safe
    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.short_description = _('permission')

    def save_model(self, request, object, form, change):
        """
        Update the permissions backend and log the event
        """
        instance = form.save(commit=False)
        instance = update_perms_and_save(request, form, instance, log=False)
        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        # Handle a special case for bulk reordering via the list view.
        if form.changed_data != ['ordering']:
            EventLog.objects.log(**log_defaults)
        return instance

    def change_view(self, request, object_id, form_url='', extra_context=None):
        result = super(TendenciBaseModelAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
        if '_addanother' not in request.POST and '_continue' not in request.POST and 'next' in request.GET:
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def log_deletion(self, request, object, object_repr):
        #application = inspect.getmodule(self).__name__
        super(TendenciBaseModelAdmin, self).log_deletion(request, object, object_repr)


def soft_delete_selected(modeladmin, request, queryset):
    """
    Replace the default delete_selected action so we can soft delete
    objects by using obj.delete() instead of queryset.delete().

    Default action which deletes the selected objects.

    This action first displays a confirmation page whichs shows all the
    deleteable objects, or, if the user has no permission one of the related
    childs (foreignkeys), a "permission denied" message.

    Next, it soft deletes all selected objects and redirects back to the change list.
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    # Populate deletable_objects, a data structure of all related objects that
    # will also be deleted.
    deletable_objects, count, perms_needed, protected = get_deleted_objects(
        queryset, request,  modeladmin.admin_site, )

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post'):
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = force_text(obj)
                modeladmin.log_deletion(request, obj, obj_display)

                # Delete the object with it's own method in case the
                # object has a custom delete method.
                obj.delete()
            modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        # Return None to display the change list page again.
        return None

    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")

    context = {
        "title": title,
        "objects_name": objects_name,
        "deletable_objects": [deletable_objects],
        'queryset': queryset,
        "perms_lacking": perms_needed,
        "protected": protected,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }

    # Display the confirmation page
    request.current_app = modeladmin.admin_site.name
    return TemplateResponse(request=request, template=[
        "admin/%s/%s/soft_delete_selected_confirmation.html" % (app_label, opts.object_name.lower()),
        "admin/%s/soft_delete_selected_confirmation.html" % app_label,
        "admin/soft_delete_selected_confirmation.html"
    ], context=context)

soft_delete_selected.short_description = _("Delete selected %(verbose_name_plural)s")

admin.site.disable_action('delete_selected')
admin.site.add_action(soft_delete_selected, 'soft_delete_selected')


class TagsFilter(SimpleListFilter):
    ##################################################
    # Adds a filter on admin sidebar to filter by tags
    ##################################################
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Tags')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        #Loads in model to get tags from
        content_type = ContentType.objects.get_for_model(model_admin.model)
        tags = TaggedItem.objects.filter(content_type=content_type).values('tag__name').distinct().order_by('tag__name')
        tags_list = []
        for tag in tags:
            tags_list.append((tag['tag__name'], tag['tag__name']))

        return tuple(tags_list)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            # Identifies individual tags based on commas and spacing
            tag = self.value().strip()
            tag_queries = [Q(tags__iexact=tag)]
            tag_queries += [Q(tags__istartswith=tag + ",")]
            tag_queries += [Q(tags__iendswith=", " + tag)]
            tag_queries += [Q(tags__iendswith="," + tag)]
            tag_queries += [Q(tags__icontains=", " + tag + ",")]
            tag_queries += [Q(tags__icontains="," + tag + ",")]
            tag_query = reduce(or_, tag_queries)
            return queryset.filter(tag_query)
        return queryset
