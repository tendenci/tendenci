from django.contrib import admin
from django.conf import settings

from perms.admin import TendenciBaseModelAdmin
from trainings.models import Training
from trainings.forms import TrainingForm

class TrainingAdmin(TendenciBaseModelAdmin):
    list_display = ['title', 'training_type', 'points', 'author_instructor','tags']
    list_filter = ['training_type']
    search_fields = ['title', 'training_type', 'description', 'author_instructor']
    fieldsets = (
        (None, 
            {'fields': (
                'title',
                'author_instructor',
                'description',
                'training_type',
                'points',
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
    form = TrainingForm

    class Media:
        js = (
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )

admin.site.register(Training, TrainingAdmin)
