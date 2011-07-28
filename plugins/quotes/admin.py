from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf import settings

from event_logs.models import EventLog
from perms.object_perms import ObjectPermission
from quotes.models import Quote
from quotes.forms import QuoteForm

class QuoteAdmin(admin.ModelAdmin):
    list_display = ['view_on_site', 'edit_link', 'quote', 'author', 'source']
    list_filter = ['author']
    search_fields = ['quote','author','source']
    fieldsets = (
        (None, {'fields': ('quote', 'author', 'source', 'tags')}),
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
    form = QuoteForm
    actions = ['update_quotes']

    def edit_link(self, obj):
        link = '<a href="%s" title="edit">Edit</a>' % reverse('admin:quotes_quote_change', args=[obj.pk])
        return link
    edit_link.allow_tags = True
    edit_link.short_description = 'edit'

    def view_on_site(self, obj):
        link_icon = '%s/images/icons/external_16x16.png' % settings.STATIC_URL
        link = '<a href="%s" title="%s"><img src="%s" /></a>' % (
            reverse('quote.view', args=[obj.pk]),
            obj.author,
            link_icon,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'

    def log_deletion(self, request, object, object_repr):
        super(QuoteAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 150300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)           

    def log_change(self, request, object, message):
        super(QuoteAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 150200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name, 
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)               

    def log_addition(self, request, object):
        super(QuoteAdmin, self).log_addition(request, object)
        log_defaults = {
            'event_id' : 150100,
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

        # set up user permission
        instance.allow_user_view, instance.allow_user_edit = form.cleaned_data['user_perms']
        
        # adding the quote
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
 
        # save the object
        instance.save()
        form.save_m2m()

        # permissions
        if not change:
            # assign permissions for selected groups
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], instance)
            # assign creator permissions
            ObjectPermission.objects.assign(instance.creator, instance) 
        else:
            # assign permissions
            ObjectPermission.objects.remove_all(instance)
            ObjectPermission.objects.assign_group(form.cleaned_data['group_perms'], instance)
            ObjectPermission.objects.assign(instance.creator, instance) 
        
        return instance

    def update_quotes(self, request, queryset):
        """
        Method to mass update and save quotes, used on text imports.
        """
        for obj in queryset:
            obj.save()

        self.message_user(request, "Quotes were successfully updated.")

    update_quotes.short_description = "Update quotes tags and index for imports"
    
    def change_view(self, request, object_id, extra_context=None):
		result = super(QuoteAdmin, self).change_view(request, object_id, extra_context)

		if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue') and request.GET.has_key('next'):
			result['Location'] = iri_to_uri("%s") % request.GET.get('next')
		return result
    
admin.site.register(Quote, QuoteAdmin)
