from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from tendenci.apps.photos.forms import PhotoSet, PhotoSetForm
from tendenci.apps.photos.models import PhotoCategory

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import update_perms_and_save
from tendenci.apps.theme.templatetags.static import static

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'update_dt', 'create_dt', 'tags', 'position')
    list_display_links = ('name',)
    list_editable = ['tags', 'position']
    fieldsets = (
        (_('Photo Set Information'), {
                      'fields': ('name',
                                 'description',
                                 'group',
                                 'tags',
                                 ),
                      }),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
            )}),
        (_('Category'), {'fields': ('cat', 'sub_cat'),
                        'classes': ['boxy-grey', 'collapse'],
            }),
        (_('Photo Set Status'), {'fields': (
            'status_detail',
        )}),
    )
    form = PhotoSetForm
    ordering = ['position']

    class Media:
        css = {
            "all": ("css/websymbols.css",)
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            '//ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js',
            static('js/admin/admin-list-reorder.js'),
        )

    def log_deletion(self, request, object, object_repr):
        super(PhotoAdmin, self).log_deletion(request, object, object_repr)
        log_defaults = {
            'event_id' : 990300,
            'event_data': '%s (%d) deleted by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s deleted' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_change(self, request, object, message):
        super(PhotoAdmin, self).log_change(request, object, message)
        log_defaults = {
            'event_id' : 990200,
            'event_data': '%s (%d) edited by %s' % (object._meta.object_name,
                                                    object.pk, request.user),
            'description': '%s edited' % object._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': object,
        }
        EventLog.objects.log(**log_defaults)

    def log_addition(self, request, object, message):
        super(PhotoAdmin, self).log_addition(request, object, message)
        log_defaults = {
            'event_id' : 990100,
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

        # update all permissions and save the model
        instance = update_perms_and_save(request, form, instance)

        # notifications
        #if not request.user.profile.is_superuser:
        #    # send notification to administrators
        #    recipients = get_notice_recipients('site', 'global', 'allnoticerecipients')
        #    if recipients:
        #        if notification:
        #            extra_context = {
        #                'object': instance,
        #                'request': request,
        #            }
        #            notification.send_emails(recipients, 'photo_added', extra_context)

        return instance


class SubCategoryAdminInline(admin.TabularInline):
    fieldsets = ((None, {'fields': ('name', 'slug')}),)
    prepopulated_fields = {'slug': ['name']}
    model = PhotoCategory
    extra = 0
    verbose_name = _("Photo Category")
    verbose_name_plural = _("Photo Categories")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'photo_categories',)
    list_display_links = ('name',)
    fieldsets = ((None, {'fields': ('name', 'slug')}),)
    prepopulated_fields = {'slug': ['name']}
    inlines = (SubCategoryAdminInline,)

    @mark_safe
    def photo_categories(self, instance):
        return ', '.join(PhotoCategory.objects.filter(parent=instance).values_list('name', flat=True))

    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.filter(parent__isnull=True)

admin.site.register(PhotoCategory, CategoryAdmin)
admin.site.register(PhotoSet, PhotoAdmin) #Image,
