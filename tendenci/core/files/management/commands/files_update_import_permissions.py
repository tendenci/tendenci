from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Updates the permission columns on the file record.
    Sets allow_anonymous_view, allow_user_view, and is_public
    to False.
    """
    def handle(self, *args, **kwargs):
        from tendenci.core.files.models import File

        File.objects.filter(
            file__startswith='files/memberships').update(
            allow_anonymous_view=False, allow_user_view=False, is_public=False)
