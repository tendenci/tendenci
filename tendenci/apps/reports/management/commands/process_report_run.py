from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Q
from django.template import TemplateDoesNotExist, Context
from django.template.loader import get_template

from johnny.cache import invalidate

from tendenci.apps.reports.utils import get_ct_nice_name


class Command(BaseCommand):
    """
    Performs a run for a report

    Usage:
        ./manage.py process_report_run 32
    """
    help = "Performs a report run based on the configuration in the report and in the run."

    def end_with_error(self, run):
        run.status = "error"
        run.complete_dt = datetime.now()
        run.save()
        invalidate('reports_run')

    def report_output_invoices(self, run):
        from tendenci.apps.invoices.models import Invoice
        from tendenci.apps.reports.models import CONFIG_OPTIONS
        results = []
        totals = {'total': 0, 'payments_credits': 0, 'balance': 0, 'count': 0}
        filters = Q()
        filters = (filters & Q(create_dt__gte=run.range_start_dt) & Q(create_dt__lte=run.range_end_dt))

        if run.report.config:
            for k, v in run.report.config_options_dict().items():
                if k in CONFIG_OPTIONS:
                    filter_kwarg = CONFIG_OPTIONS[k]['options'][v]['filter']
                    if filter_kwarg:
                        filters = (filters & Q(**filter_kwarg))
                elif k == "invoice_object_type":
                    if "None" in v:
                        v.pop(v.index("None"))
                        filters = (filters & (Q(object_type__in=v) | Q(object_type__isnull=True)))
                    else:
                        filters = (filters & Q(object_type__in=v))

        distinct_object_types = Invoice.objects.filter(filters).values('object_type').distinct()

        for ot in distinct_object_types:
            ot_dict = {}
            invoices = Invoice.objects.filter(filters).filter(
                object_type=ot['object_type'])
            ot_dict['invoices'] = invoices.order_by('create_dt')
            ot_dict['object_type'] = get_ct_nice_name(ot['object_type'])
            ot_dict['count'] = invoices.count()
            aggregates = invoices.aggregate(Sum('total'), Sum('payments_credits'), Sum('balance'))
            ot_dict.update(aggregates)
            results.append(ot_dict)
            totals['count'] = totals['count'] + ot_dict['count']
            totals['total'] = totals['total'] + aggregates['total__sum']
            totals['payments_credits'] = totals['payments_credits'] + aggregates['payments_credits__sum']
            totals['balance'] = totals['balance'] + aggregates['balance__sum']

        results = sorted(results, key=lambda k: k['object_type'])

        try:
            t = get_template("reports/invoices/results.html")
        except TemplateDoesNotExist:
            self.end_with_error(run)
            raise CommandError('The template for this report is missing.')
        return t.render(Context({
            'results': results,
            'totals': totals,
            'run': run}))

    def handle(self, *args, **options):
        from tendenci.apps.reports.models import Run
        try:
            run_id = args[0]
        except Exception:
            raise CommandError('You need to pass a report run as an argument.')

        try:
            run = Run.objects.get(pk=run_id)
        except (Run.DoesNotExist, Run.MultipleObjectsFound):
            raise CommandError('The Run %s could not be found in the database.' % run_id)

        if run.status == "unstarted":
            run.status = "running"
            run.start_dt = datetime.now()
            run.save()
            invalidate('reports_run')

            print "running report"

            report_output = "Report Output Here"
            run.output = report_output

            if run.report.type == "invoices":
                run.output = self.report_output_invoices(run=run)

            print "report complete"
            if not run.status == "error":
                run.status = "complete"

            run.complete_dt = datetime.now()
            run.save()
            invalidate('reports_run')

        else:
            print "Report is already running"
