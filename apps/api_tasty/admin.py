from django.contrib import admin

from tastypie.models import ApiKey

from api_tasty.forms import ApiKeyForm

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'created']
    form = ApiKeyForm

admin.site.register(ApiKey, ApiKeyAdmin)
