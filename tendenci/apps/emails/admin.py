from django.contrib import admin

from .models import Email


class EmailAdmin(admin.ModelAdmin):
    model = Email
    list_display = ['id', 'subject', 'sender']
    list_display_links = ['subject']


admin.site.register(Email, EmailAdmin)
