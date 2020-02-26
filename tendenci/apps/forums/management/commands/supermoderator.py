

from django.core.management.base import BaseCommand, CommandError
from tendenci.apps.forums import compat

from tendenci.apps.forums.models import Forum


class Command(BaseCommand):
    help = 'Set and remove moderator to all forums'
    args = '{add|del} username'

    def handle(self, *args, **kwargs):
        if len(args) != 2:
            raise CommandError("Enter action {add|del} and username")
        action, username = args
        assert action in ('add', 'del')
        user = compat.get_user_model().objects.get(**{compat.get_username_field(): username})
        forums = Forum.objects.all()
        for forum in forums:
            forum.moderators.remove(user)
            if action == 'add':
                forum.moderators.add(user)
