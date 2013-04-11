import inspect
from operator import or_

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from tagging.models import TaggedItem
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save


class TendenciBaseModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin class to help with event logs
    """

    class Media:
        js = ('%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,)

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

        self.list_display_links = ('edit_link', )

    def edit_link(self, obj):
        return "Edit"
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%simages/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            obj.get_absolute_url(),
            obj,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def owner_link(self, obj):
        link = ''
        if obj.owner_username:
            link = '<a href="%s" title="%s">%s</a>' % (
                reverse('profile', args=[obj.owner_username]),
                obj.owner_username,
                obj.owner_username,
            )
        return link
    owner_link.allow_tags = True
    owner_link.short_description = 'owner'

    def admin_status(self, obj):
        return obj.obj_status
    admin_status.allow_tags = True
    admin_status.short_description = 'status'

    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.allow_tags = True
    admin_perms.short_description = 'permission'

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
        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def log_deletion(self, request, object, object_repr):
        application = inspect.getmodule(self).__name__
        super(TendenciBaseModelAdmin, self).log_deletion(request, object, object_repr)

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
