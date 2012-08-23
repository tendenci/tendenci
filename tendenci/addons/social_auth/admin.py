"""Admin settings"""
from django.contrib import admin
from tendenci.core.registry import admin_registry

from tendenci.addons.social_auth.models import UserSocialAuth, Nonce, Association


class UserSocialAuthOption(admin.ModelAdmin):
    """Social Auth user options"""
    list_display = ('id', 'user', 'provider', 'uid')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_filter = ('provider',)
    raw_id_fields = ('user',)
    list_select_related = True


class NonceOption(admin.ModelAdmin):
    """Nonce options"""
    list_display = ('id', 'server_url', 'timestamp', 'salt')
    search_fields = ('server_url',)


class AssociationOption(admin.ModelAdmin):
    """Association options"""
    list_display = ('id', 'server_url', 'assoc_type')
    list_filter = ('assoc_type',)
    search_fields = ('server_url',)


admin_registry.site.register(UserSocialAuth, UserSocialAuthOption)
admin_registry.site.register(Nonce, NonceOption)
admin_registry.site.register(Association, AssociationOption)
