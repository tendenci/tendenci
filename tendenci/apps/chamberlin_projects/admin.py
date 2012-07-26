from django.contrib import admin
from django.conf import settings

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.chamberlin_projects.models import Project, ConstructionType, ConstructionActivity, ConstructionCategory
from tendenci.apps.chamberlin_projects.forms import ProjectForm

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}

class ProjectAdmin(TendenciBaseModelAdmin):
    list_display = [u'title', 'tags']
    list_filter = []
    search_fields = []
    actions = []
    prepopulated_fields = {'slug': ['title']}

    form = ProjectForm

    fieldsets = (
        (None, 
            {'fields': (
                'title',
                'slug',
                'location',
                'city',
                'state',
                'construction_type',
                'construction_activity',
                'category',
                'contract_amount',
                'owner_name',
                'architect',
                'general_contractor',
                'scope_of_work',
                'project_description',
                'tags',
            )}
        ),
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
        )

admin.site.register(Project, ProjectAdmin)
admin.site.register(ConstructionType)
admin.site.register(ConstructionActivity)
admin.site.register(ConstructionCategory, CategoryAdmin)
