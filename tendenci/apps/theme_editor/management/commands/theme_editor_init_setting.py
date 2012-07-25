from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Updates site_settings_setting table w/ initial theme
    """
    def handle(self, *args, **options):
        from django.conf import settings
        from tendenci.apps.site_settings.models import Setting
        from django.core.cache import cache

        setting = Setting.objects.get(scope='module', scope_category='theme_editor')
        setting.set_value(settings.SITE_THEME)
        setting.save()
        cache.clear()
