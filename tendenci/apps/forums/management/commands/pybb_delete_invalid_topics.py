

from builtins import input

from django.utils.timezone import now, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Count

from tendenci.apps.forums.models import Topic

class Command(BaseCommand):
    help = 'Resave all posts.'

    def handle(self, *args, **kwargs):
        check_time = now() - timedelta(seconds=10)
        topics = Topic.objects.filter(created__lt=check_time)\
                      .annotate(counter=Count('posts'))\
                      .filter(counter=0)

        count = topics.count()
        print('Found %d invalid topics' % count)
        if count:
            answer = input('Are you sure you want delete them? [y/n]:')
            if answer.lower() == 'y':
                print('Deleting topics')
                topics.delete()
                print('Deletion completed')
            else:
                print('Aborting')
