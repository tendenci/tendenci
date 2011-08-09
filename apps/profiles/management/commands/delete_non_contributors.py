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
        from directories.models import Directory
        from articles.models import Article
        from events.models import Event
        from photos.models import Photo
        from pages.models import Page
        from news.models import News

        contribs = []

        for directory in Directory.objects.all():
            contribs.append(directory.creator)
            contribs.append(directory.owner)

        for article in Article.objects.all():
            contribs.append(article.creator)
            contribs.append(article.owner)

        for event in Event.objects.all():
            contribs.append(event.creator)
            contribs.append(event.owner)

        for photo in Photo.objects.all():
            contribs.append(photo.creator)
            contribs.append(photo.owner)

        for page in Page.objects.all():
            contribs.append(page.creator)
            contribs.append(page.owner)

        for news in News.objects.all():
            contribs.append(news.creator)
            contribs.append(news.owner)

        contribs = list(set(contribs))  # remove duplicates
        slackers = User.objects.exclude(username__in=[c.username for c in contribs])

        print 'contribs', len(contribs)
        print 'slackers', slackers.count()
        print 'everyone', User.objects.count()
        print 'Pass the -d or --delete fn to delete no contributors'

        delete = options['delete']

        if delete:
            for slacker in slackers:
                print slacker
                slacker.delete()