from django.contrib import admin

from .models import Email


class EmailAdmin(admin.ModelAdmin):
    model = Email


admin.site.register(Email, EmailAdmin)
