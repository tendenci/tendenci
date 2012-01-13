from django.contrib import admin
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse

from before_and_after.models import BeforeAndAfter, Category, \
    Subcategory, PhotoSet
from before_and_after.forms import BnAForm
from perms.utils import update_perms_and_save
from event_logs.models import EventLog

class PhotoSetAdmin(admin.StackedInline):
    model = PhotoSet
    extra = 1
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "warning"]
    list_filter = ["category", "warning"]

class BnAAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', "title", "category", "subcategory", 'admin_notes','ordering']
    list_filter = ["category", "subcategory"]
    form = BnAForm
    ordering = ['-ordering']
    list_editable = ['ordering']
    inlines = [PhotoSetAdmin,]
    
    fieldsets = (
        (None, {'fields': (
            'title',
            'category',
            'subcategory',
            'description',
            'tags',
            'admin_notes',
        )}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',),'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status',
            'status_detail'
        )}),
    )
            
    class Media:
        js = (
            '%sjs/admin/sortable_inline/jquery-1.5.1.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/jquery-ui-1.8.13.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/sortable_inline/stacked-sort.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.2.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )
    
    def view_on_site(self, obj):
        link_icon = '%s/images/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('before_and_after.detail', args=[obj.pk]),
            obj.title,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
    
    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:before_and_after_beforeandafter_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'
        
    def log_deletion(self, request, object, object_repr):
        super(BnAAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 1090300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(BnAAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 1090200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(BnAAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 1090100,
            'event_data': '%s (%d) added by %s' % (object._meta.object_name, 
                                                   object.pk, request.user),
            'description': '%s added' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)
                     
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(BnAAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, object, form, change):
        """
        update the permissions backend
        """
        instance = form.save(commit=False)
        perms = update_perms_and_save(request, form, instance)
        return instance

    def change_view(self, request, object_id, extra_context=None):
		result = super(BnAAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result

admin.site.register(BeforeAndAfter, BnAAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
