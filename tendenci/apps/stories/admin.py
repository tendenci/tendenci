from django.contrib import admin
from tendenci.core.registry import admin_registry
from tendenci.apps.stories.models import Story

admin_registry.site.register(Story)