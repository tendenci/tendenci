from django.contrib import admin
from django.conf import settings

from attorneys.models import Attorney, Photo
from attorneys.forms import AttorneyForm, PhotoForm

class PhotoInline(admin.StackedInline):
    model = Photo
    form = PhotoForm
    fieldsets = (
        (None, {'fields': (
            'file',
        )}),
    )
    extra = 0;

class AttorneyAdmin(admin.ModelAdmin):
    class Meta:
        model = Attorney
        
    list_display = ["last_name", "first_name", "position", "category"]
    list_filter = ["category"]
    form = AttorneyForm
    inlines = [PhotoInline,]
    
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
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.creator = request.user
                instance.creator_username = request.user.username
            instance.owner = request.user
            instance.owner_username = request.user.username
            instance.save()
    
    def get_form(self, request, obj=None, **kwargs):
        """
        inject the user in the form.
        """
        form = super(AttorneyAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

admin.site.register(Attorney, AttorneyAdmin)
