from django.conf import settings as d_settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    """
    Example: python manage.py set_setting site global siteurl http://example.com
    """

    def handle(self, scope=None, scope_category=None, name=None, value=None, **options):
        """
        Set the website theme via theme name
        """
        from tendenci.core.site_settings.models import Setting
        from tendenci.core.site_settings.utils import delete_all_settings_cache

        if scope and scope_category and name and value:
            try:
                setting = Setting.objects.get(
                    name=name,
                    scope=scope,
                    scope_category=scope_category,
                )
                setting.set_value(value)
                setting.save()

            except Setting.DoesNotExist:
                if int(options['verbosity']) > 0:
                    print "We could not update that setting."
            delete_all_settings_cache()

            if name == "sitedisplayname":
                from tendenci.apps.user_groups.models import Group
                from tendenci.apps.entities.models import Entity
                try:
                    entity = Entity.objects.get(pk=1)
                    entity.entity_name = value
                    entity.save()
                except:
                    pass

                try:
                    group = Group.objects.get(pk=1)
                    group.name = value
                    group.label = value
                    group.slug = ''
                    group.save()
                except:
                    pass
