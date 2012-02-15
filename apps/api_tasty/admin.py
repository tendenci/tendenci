from django.contrib import admin

from tastypie.models import ApiKey

from api_tasty.forms import ApiKeyForm

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'created']
    form = ApiKeyForm

# already registered in a more recent version of tasty pie
#admin.site.register(ApiKey, ApiKeyAdmin)
