from django.contrib import admin

from perms.admin import TendenciBaseModelAdmin
from quotes.models import Quote
from quotes.forms import QuoteForm

class QuoteAdmin(TendenciBaseModelAdmin):
    list_display = ['quote', 'author', 'source']
    list_filter = ['author']
    search_fields = ['quote','author','source']
    fieldsets = (
        (None, {'fields': ('quote', 'author', 'source', 'tags')}),
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
    form = QuoteForm
    actions = ['update_quotes']

    def update_quotes(self, request, queryset):
        """
        Mass update and save quotes, used on text imports.
        """
        for obj in queryset:
            obj.save(log=False)

        self.message_user(request, "Quotes were successfully updated.")

    update_quotes.short_description = "Update quotes tags and index for imports"

admin.site.register(Quote, QuoteAdmin)
