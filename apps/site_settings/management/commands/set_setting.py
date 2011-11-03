from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Example: python manage.py set_setting site developer freepaid paid
    """

    def handle(self, scope=None, scope_category=None, name=None, value=None, **options):
        """
        Set the website theme via theme name
        """
        from site_settings.models import Setting
        if scope and scope_category and name and value:
            try:
                setting = Setting.objects.filter(
                    name=name,
                    scope=scope,
                    scope_category=scope_category,
                ).update(value=value)
            except:
                if int(options['verbosity']) > 0:
                    print "We could not update that setting."