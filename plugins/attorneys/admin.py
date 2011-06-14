from django.contrib import admin
from django.conf import settings

from attorneys.models import Attorney
from attorneys.forms import AttorneyForm

class AttorneyAdmin(admin.ModelAdmin):
    class Meta:
        model = Attorney
    list_display = ["last_name", "first_name", "position", "category"]
    list_filter = ["category"]
    form = AttorneyForm
    
    fieldsets = (
        (None, {'fields': (
            'first_name',
            'last_name',
            'category',
            'position',
            'address',
            'address2',
            'city',
            'state',
            'zip',
            'phone',
            'fax',
            'email',
            'bio',
            'education',
            'casework',
            'admissions',
            'photo',
            'tags',
        )}),
        ('Administrative', {'fields': (
            'allow_anonymous_view',
            'status',
            'status_detail',
            'group_perms',
            'user_perms',
        )}),
    )
            
    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
        
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(AttorneyAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

admin.site.register(Attorney, AttorneyAdmin)
