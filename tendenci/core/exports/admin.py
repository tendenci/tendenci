from django.contrib import admin
from tendenci.core.registry import admin_registry
from tendenci.core.exports.models import Export

admin_registry.site.register(Export)
