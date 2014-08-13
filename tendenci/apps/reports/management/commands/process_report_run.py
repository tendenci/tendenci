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
        from tendenci.addons.corporate_memberships.models import CorpMembership
        try:
            from donations.models import Donation
        except:
            Donation = None
        from tendenci.addons.memberships.models import (MembershipType,
            MembershipSet, MembershipDefault)
        from tendenci.apps.invoices.models import Invoice
        from tendenci.apps.reports.models import CONFIG_OPTIONS
        is_summary_mode = (run.output_type == 'html-summary')
        results = []
        totals = {'total': 0, 'payments_credits': 0, 'balance': 0, 'count': 0}
        filters = Q()
        filters = (filters & Q(create_dt__gte=run.range_start_dt) & Q(create_dt__lte=run.range_end_dt))

        membership_filter = None

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
                elif k == "invoice_membership_filter":
                    try:
                        item = MembershipType.objects.get(pk=v)
                        membership_filter = item
                    except:
                        pass

        distinct_object_types = Invoice.objects.filter(filters).values('object_type').distinct()

        for ot in distinct_object_types:
            ot_dict = {}
            invoices = Invoice.objects.filter(filters).filter(
                object_type=ot['object_type'])

            try:
                if membership_filter:
                    invoice_object = invoices[0].get_object()

                    if isinstance(invoice_object, MembershipDefault):
                        members_pk = MembershipDefault.objects.filter(membership_type=membership_filter) \
                            .values_list('pk', flat=True)
                        invoices = invoices.filter(object_id__in=set(members_pk))
                    elif isinstance(invoice_object, MembershipSet):
                        members_pk = MembershipSet.objects.filter(membershipdefault__membership_type=membership_filter) \
                            .values_list('pk', flat=True)
                        invoices = invoices.filter(object_id__in=set(members_pk))
                    elif isinstance(invoice_object, CorpMembership):
                        members_pk = CorpMembership.objects.filter(corporate_membership_type__membership_type=membership_filter) \
                            .values_list('pk', flat=True)
                        invoices = invoices.filter(object_id__in=set(members_pk))
            except:
                pass

            # generate summary mode data
            if is_summary_mode:
                sm_dict = {}
                for invoice in invoices:
                    key = str(invoice.get_object())
                    if key not in sm_dict:
                        sm_dict[key] = {
                            'invoices': [],
                            'count': 0,
                            'total': 0,
                            'payments_credits': 0,
                            'balance': 0,
                        }
                    invoice_dict = sm_dict[key]
                    invoice_dict['count'] += 1
                    invoice_dict['invoices'].append(invoice)
                    invoice_dict['total'] += invoice.total
                    invoice_dict['payments_credits'] += invoice.payments_credits
                    invoice_dict['balance'] += invoice.balance
                ot_dict['summary'] = [v for k,v in sm_dict.items()]

            ot_dict['invoices'] = invoices.order_by('create_dt')
            ot_dict['object_type'] = get_ct_nice_name(ot['object_type'])
            ot_dict['count'] = invoices.count()
            ot_dict.update({
                'is_membership': 'membership' in ot_dict['object_type'].lower(),
                'is_donation': 'donation' in ot_dict['object_type'].lower(),
                })

            aggregates = invoices.aggregate(Sum('total'), Sum('payments_credits'), Sum('balance'))
            for k, v in aggregates.items():
                if not v: aggregates[k] = v or 0

            ot_dict.update(aggregates)
            results.append(ot_dict)
            totals['count'] = totals['count'] + ot_dict['count']
            totals['total'] = totals['total'] + aggregates['total__sum']
            totals['payments_credits'] = totals['payments_credits'] + aggregates['payments_credits__sum']
            totals['balance'] = totals['balance'] + aggregates['balance__sum']

        results = sorted(results, key=lambda k: k['object_type'])

        try:
            if run.output_type == 'html-extended':
                t = get_template("reports/invoices/results-extended.html")
            elif is_summary_mode:
                t = get_template("reports/invoices/results-summary.html")
            else:
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
        except (Run.DoesNotExist, Run.MultipleObjectsReturned):
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
