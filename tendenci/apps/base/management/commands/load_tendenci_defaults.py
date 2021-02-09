

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Insert default data"

    def add_arguments(self, parser):
        parser.add_argument('--reset-nav',
            action="store_true", dest='reset_nav', default=False,
            help='Reset the navigation')

    def handle(self, **options):
        """
        Load data from tendenci default fixtures
        """
        reset_nav = options.get('reset_nav', None)
        self.number_used = []

        self.call_loaddata(reset_nav)

    def call_loaddata(self, reset_nav=False):
        """
        This calls the loaddata command on all default fixtures.
        """
        if reset_nav:
            from tendenci.apps.navs.models import NavItem
            try:
                main_nav_items = NavItem.objects.filter(nav_id=1)
                main_nav_items.delete()
            except:
                pass

        print('tendenci_default_auth_user.json')
        call_command('loaddata', 'tendenci_default_auth_user.json')
        print('tendenci_default_auth_groups.json')
        call_command('loaddata', 'tendenci_default_auth_groups.json')
        print('tendenci_default_entities.json')
        call_command('loaddata', 'tendenci_default_entities.json')
        print('tendenci_default_user_groups.json')
        call_command('loaddata', 'tendenci_default_user_groups.json')
        print('tendenci_default_files.json')
        call_command('loaddata', 'tendenci_default_files.json')
        print('load tendenci_default_paymentmethod.json')
        call_command('loaddata', 'tendenci_default_paymentmethod.json')
        print('load tendenci_default_forums.json')
        call_command('loaddata', 'tendenci_default_forums.json')
        print('load tendenci_default_regions_region.json')
        call_command('loaddata', 'tendenci_default_regions_region.json')
        print('load tendenci_default_directories_pricings.json')
        call_command('loaddata', 'tendenci_default_directories_pricings.json')

        suffix_list = [
            'profiles_profile',
            'explorer',
            'events',
            'jobs',
            'memberships',
            'corporate_memberships',
            'articles',
            'forms',
            'forums',
            'news',
            'photos',
            'boxes',
            'pages',
            'navs',
            'stories',
            'videos',
            'industries'
        ]

        # call loaddata on fixtures
        for suffix in suffix_list:
            filename = 'tendenci_default_%s.json' % suffix

            print(filename)
            call_command('loaddata', filename)
