from django.contrib import admin

from perms.models import ObjectPermission
from models import Topic, HelpFile, Request
from forms import HelpFileForm

class HelpFileAdmin(admin.ModelAdmin):
    list_display = ['question', 'level', 'is_faq', 'is_featured', 'is_video', 'syndicate', 'view_totals']
    list_filter = ['topics', 'level', 'is_faq', 'is_featured', 'is_video', 'syndicate']
    filter_horizontal = ['topics']
    search_fields = ['question','answer']
    fieldsets = (
        (None, {'fields': ('question', 'answer', 'level','topics','entity')}),
        ('Flags', {'fields': (
            ('is_faq', 'is_featured', 'is_video', 'syndicate'),)}),
        ('Administrative', {'fields': (
            'allow_anonymous_view','status','status_detail' )}),
    )
    form = HelpFileForm
    
    def save_model(self, request, object, form, change):
        instance = form.save(commit=False)
        
        # adding the helpfile
        if not change:
            instance.creator = request.user
            instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
        
        # save the object
        instance.save()
        form.save_m2m()

        if not change:
            # assign permissions for selected users
            ObjectPermission.objects.assign(instance.creator, instance)
        
        return instance
    
admin.site.register(Topic)
admin.site.register(HelpFile, HelpFileAdmin)
admin.site.register(Request)
