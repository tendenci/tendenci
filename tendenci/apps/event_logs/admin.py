from django.contrib import admin
from tendenci.apps.event_logs.models import EventLog, EventLogColor, EventLogBaseColor


class EventLogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'create_dt', 'content_type', 'object_id', 'event_id',
                    'headline', 'description', 'source',
                    'event_name', 'event_type', 'category']
    list_filter = ['source', 'event_id', 'event_name', 'event_type', 'category', 'content_type']

    date_hierarchy = 'create_dt'


class EventLogColorAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'color']

    def color(self, obj):
        return '<span style="background-color: #%s"> #%s </span> ' % (obj.hex_color, obj.hex_color)
    color.allow_tags = True


class EventLogBaseColorAdmin(EventLogColorAdmin):
    list_display = ['source', 'event_id', 'color']


#admin.site.register(EventLog, EventLogAdmin)
#admin.site.register(EventLogColor, EventLogColorAdmin)
#admin.site.register(EventLogBaseColor, EventLogBaseColorAdmin)