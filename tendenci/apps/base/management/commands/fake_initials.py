from __future__ import print_function
import traceback
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    """
    This is the first command you should run when migrating db from t6 to t7.
    It fakes all initials.
    The --fake-initial option of the migrate command doesn't work well, therefore,
    it cannot replace this command.
    """
    def handle(self, *args, **options):
        try:
            call_command('migrate', 'contenttypes', '0001', '--fake')
        except:
            pass
        try:
            call_command('migrate', 'contenttypes')
        except:
            # might need to fake 0002
            call_command('migrate', 'contenttypes', '0002', '--fake')
        try:
            call_command('migrate', 'auth', '0001', '--fake')
            call_command('migrate', 'auth')
        except:
            pass

        apps = ('admin',
                'user_groups',
                'entities',
                'accountings',
                'announcements',
                'articles',
                'base',
                'boxes',
                'campaign_monitor',
                'captcha',
                'careers',
                'case_studies',
                'categories',
                'committees',
                'contacts',
                'contributions',
                'corporate_memberships',
                'dashboard',
                'directories',
                'discounts',
                'donations',
                'educations',
                'email_blocks',
                'emails',
                'event_logs',
                'events',
                'explorer',
                'explorer_extensions',
                'exports',
                'files',
                'forms',
                'handler404',
                'help_files',
                'ics',
                'imports',
                'industries',
                'invoices',
                'jobs',
                'locations',
                'make_payments',
                'memberships',
                'meta',
                'metrics',
                'navs',
                'news',
                'newsletters',
                'notifications',
                'pages',
                'payments',
                'perms',
                'photos',
                'profiles',
                'recurring_payments',
                'redirects',
                'regions',
                'registration',
                'reports',
                'resumes',
                'robots',
                'search',
                'sessions',
                'site_settings',
                'sites',
                'social_auth',
                'speakers',
                'staff',
                'stories',
                'studygroups',
                'tagging',
                'tendenci_guide',
                'testimonials',
                'theme_editor',
                'versions',
                'videos',
                'wp_exporter',
                'wp_importer',
                'djcelery',
                'tastypie'
                )
        for a in apps:
            try:
                call_command('migrate', a, '0001', '--fake')
            except:
                print(traceback.format_exc())
