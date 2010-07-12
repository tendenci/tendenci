from django.contrib import admin
from event_logs.models import EventLog

class EventLogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'content_type', 'object_id', 'source', 
                    'event_id', 'event_name', 'event_type', 'category']
    list_filter = ['source', 'event_id', 'event_name', 'event_type', 'category', 'content_type']
    
    date_hierarchy = 'create_dt'

admin.site.register(EventLog, EventLogAdmin)