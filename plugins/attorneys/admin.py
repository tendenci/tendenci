from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from perms.admin import TendenciBaseModelAdmin
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

class AttorneyAdmin(TendenciBaseModelAdmin):
    class Meta:
        model = Attorney
        
    list_display = ["last_name", "first_name", "position", "category", "ordering"]
    list_filter = ["category"]
    prepopulated_fields = {'slug': ['first_name','last_name']}
    form = AttorneyForm
    ordering = ['ordering']
    list_editable = ['ordering']
    inlines = [PhotoInline,]
    
    fieldsets = (
        (None, {'fields': (
            'first_name',
            'middle_initial',
            'last_name',
            'slug',
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
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.2.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
        )

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            file = f.save(commit=False)
            if file.file:
                file.attorney = form.save()
                file.content_type = ContentType.objects.get_for_model(file.attorney)
                file.object_id = file.attorney.pk
                file.name = file.file.name
                file.creator = request.user
                file.owner = request.user
                file.save(log=False)

        formset.save()

admin.site.register(Attorney, AttorneyAdmin)
