from django.contrib import admin
from models import Topic, HelpFile, Request

class HelpFileAdmin(admin.ModelAdmin):
    filter_horizontal = ['topics']
    fieldsets = (
        (None, {'fields': (
            ('entity', 'level'), 'question', 'answer', 'topics')}),
        ('Flags', {'fields': (
            ('is_faq', 'is_featured', 'is_video', 'is_syndicated'),)}),
        ('Stats', {'fields': (
            'view_totals', )}),
    )

admin.site.register(Topic)
admin.site.register(HelpFile, HelpFileAdmin)
admin.site.register(Request)
