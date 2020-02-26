
import subprocess
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.conf import settings

from tendenci.apps.metrics.models import Metric


class Command(BaseCommand):
    """
    Gather usage statistics about the site

    Statistics gathered:

    1. HDD space used from the shell
    2. Total users from auth_users
    3. Total members from auth_users
    4. Total visits from event_logs by day
    5. Total number of invoices from invoices
    6. Total number of positive invoices (total > 0)
    7. Sum of total field for invoices
    """
    def handle(self, *app_names, **options):
        """
        Handle gathering the statistics
        """
        verbosity = 1
        if 'verbosity' in options:
            verbosity = int(options['verbosity'])

        # cache the user/member totals
        self.users = self.get_users()
        self.members = self.get_members()

        # create a metric from the totals
        metric = Metric()
        metric.users = len(self.users)
        if self.members:
            metric.members = len(self.members)
        else:
            metric.members = 0
        metric.visits = len(self.get_visits())
        metric.disk_usage = self.get_site_size()
        metric.invoices = self.get_invoices().count()
        metric.positive_invoices = self.get_positive_invoices().count()
        metric.invoice_totals = Decimal(self.get_invoice_totals())

        if verbosity >= 2:
            print('metric.users', metric.users)
            print('metric.members', metric.members)
            print('metric.visits', metric.visits)
            print('metric.disk_usage', metric.disk_usage)
            print('metric.invoices', metric.invoices)
            print('metric.positive_invoices', metric.positive_invoices)
            print('metric.invoice_totals', metric.invoice_totals)

        metric.save()

    def get_users(self):
        """
        Get all users from the profiles_profile table
        """
        from tendenci.apps.profiles.models import Profile

        return Profile.objects.filter(status_detail="active", status=True)

    def get_members(self):
        """
        Get all members from the memberships_membership table
        """
        try:
            from tendenci.apps.memberships.models import MembershipDefault

            return MembershipDefault.objects.active()
        except ImportError:
            pass

    def get_visits(self):
        """
        Get all visits that are not bots from event_logs

        1. Filter the visits by this month only
        2. Filter the visits by non-bots
        """
        from tendenci.apps.event_logs.models import EventLog
        today = date.today()

        # if the script runs today, we collect the data from yesterday
        yesterday = today - timedelta(days=1)

        filters = {
            'robot__exact': None,
            'create_dt__range': (yesterday, today)
        }

        return EventLog.objects.filter(**filters)

    def get_site_size(self):
        """
        Get the HDD usage of the entire site
        """
        cmd = 'du -s -k %s' % settings.PROJECT_ROOT
        size_in_kb = 0
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            size_in_kb = int(output.split()[0].strip())
        except subprocess.CalledProcessError:
            pass

        return size_in_kb * 1024

    def get_invoices(self):
        """
        Get all invoices from the invoices_invoice table
        """
        from tendenci.apps.invoices.models import Invoice
        today = date.today()

        # if the script runs today, we collect the data from yesterday
        yesterday = today - timedelta(days=1)

        filters = {
            'status_detail': 'tendered',
            'create_dt__range': (yesterday, today)
        }

        return Invoice.objects.filter(**filters)

    def get_positive_invoices(self):
        """
        Get all invoices that have a total that is greater than 0
        """
        return self.get_invoices().filter(total__gt=0)

    def get_invoice_totals(self):
        """
        Get the sum of all invoice totals
        """
        # if there are no invoices, we return 0 for our decimal field
        return self.get_invoices().aggregate(Sum('total'))['total__sum'] or 0
