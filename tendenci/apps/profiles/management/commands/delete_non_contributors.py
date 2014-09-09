from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    """
    Get/Delete list of contributors, non-contributors and total users
    """

    option_list = BaseCommand.option_list + (
        make_option('-d', '--delete',
        action='store_true',
        default=False,
        help='Delete non contributing users'),
    )

    def handle(self, *args, **options):
        from django.contrib.auth.models import User

        contribs = []

        try:
            from tendenci.apps.directories.models import Directory
            for directory in Directory.objects.all():
                contribs.append(directory.creator)
                contribs.append(directory.owner)
        except ImportError:
            pass

        try:
            from tendenci.apps.articles.models import Article
            for article in Article.objects.all():
                contribs.append(article.creator)
                contribs.append(article.owner)
        except ImportError:
            pass

        try:
            from tendenci.apps.events.models import Event
            for event in Event.objects.all():
                contribs.append(event.creator)
                contribs.append(event.owner)
        except ImportError:
            pass

        try:
            from tendenci.apps.photos.models import Photo
            for photo in Photo.objects.all():
                contribs.append(photo.creator)
                contribs.append(photo.owner)
        except ImportError:
            pass

        try:
            from tendenci.apps.pages.models import Page
            for page in Page.objects.all():
                contribs.append(page.creator)
                contribs.append(page.owner)
        except ImportError:
            pass

        try:
            from tendenci.apps.news.models import News
            for news in News.objects.all():
                contribs.append(news.creator)
                contribs.append(news.owner)
        except ImportError:
            pass

        contribs = list(set(contribs))  # remove duplicates
        slackers = User.objects.exclude(username__in=[c.username for c in contribs if c])

        print 'contribs', len(contribs)
        print 'slackers', slackers.count()
        print 'everyone', User.objects.count()
        print 'Pass the -d or --delete fn to delete no contributors'

        delete = options['delete']

        if delete:
            from django.db import connections, DEFAULT_DB_ALIAS, IntegrityError
            using = options.get('database', DEFAULT_DB_ALIAS)
            connection = connections[using]
            cursor = connection.cursor()

            cursor.execute('SET FOREIGN_KEY_CHECKS=0;')
            for slacker in slackers:
                try:
                    print slacker
                    slacker.delete()
                except IntegrityError as e:
                    print 'Integrity Error deleting', slacker

            cursor.execute('SET FOREIGN_KEY_CHECKS=1;')