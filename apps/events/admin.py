from django.contrib import admin
from events.models import Event, Type
from events.forms import EventForm

class EventAdmin(admin.ModelAdmin):
#    form = EventForm
    list_display=(
        'title',
        'description', 
        'start_dt',
        'end_dt',
        'timezone',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',
        'status',
        'status_detail',
    )

admin.site.register(Event, EventAdmin)
admin.site.register(Type)