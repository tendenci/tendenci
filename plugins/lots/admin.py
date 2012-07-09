from django.contrib import admin
from django.conf import settings

from perms.admin import TendenciBaseModelAdmin
from lots.models import Lot, Map, Line
from lots.forms import LotForm, MapForm

class LineInline(admin.TabularInline):
    model = Line

class LotAdmin(TendenciBaseModelAdmin):
    list_display = ['name', 'tags']
    list_filter = []
    search_fields = []
    actions = []
    inlines = [
        LineInline,
    ]
    
    form = LotForm
    
    fieldsets = (
        (None, 
            {'fields': (
                'map',
                'name',
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

class MapAdmin(TendenciBaseModelAdmin):
    list_display = ['name',]
    list_filter = []
    search_fields = []
    actions = []
    
    form = MapForm
    
    fieldsets = (
        (None, 
            {'fields': (
                'name',
                'file',
                'description',
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
