from __future__ import print_function
import commands
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from django.conf import settings

from tendenci.apps.metrics.models import Metric


class Command(BaseCommand):
    """
    Update the invoice fields in past metric records
    """
    def handle(self, *app_names, **options):
        """
        Grab metrics without invoice data and retrieve that data
        """
        verbosity = 1
        if 'verbosity' in options:
            verbosity = int(options['verbosity'])


        metrics = Metric.objects.filter(invoices__isnull=True)
        for metric in metrics:
            metric.invoices = self.get_invoices(metric.create_dt).count()
            metric.positive_invoices = self.get_positive_invoices(metric.create_dt).count()
            metric.invoice_totals = Decimal(self.get_invoice_totals(metric.create_dt))

            if verbosity >= 2:
                print('metric.create_dt', metric.create_dt)
                print('metric.invoices', metric.invoices)
                print('metric.positive_invoices', metric.positive_invoices)
                print('metric.invoice_totals', metric.invoice_totals)

            metric.save()

    def get_invoices(self, metric_date):
        """
        Get all invoices from the invoices_invoice table
        """
        from tendenci.apps.invoices.models import Invoice
        today = metric_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # if the script runs today, we collect the data from yesterday
        yesterday = today - timedelta(days=1)

        filters = {
            'status_detail': 'tendered',
            'create_dt__range': (yesterday, today)
        }

        return Invoice.objects.filter(**filters)

    def get_positive_invoices(self, metric_date):
        """
        Get all invoices that have a total that is greater than 0
        """
        return self.get_invoices(metric_date).filter(total__gt=0)

    def get_invoice_totals(self, metric_date):
        """
        Get the sum of all invoice totals
        """
        # if there are no invoices, we return 0 for our decimal field
        return self.get_invoices(metric_date).aggregate(Sum('total'))['total__sum'] or 0
