from builtins import str
from collections import OrderedDict

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import simplejson as json

from tendenci.apps.memberships.models import MembershipType
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.reports.utils import get_ct_nice_name


REPORT_TYPE_CHOICES = (
    ('invoices', "Invoices"),
)


CONFIG_OPTIONS = {
    'invoice_display': {
        "label": "Which invoices",
        "options": OrderedDict(sorted({
            'all': {
                "label": 'All Invoices',
                "filter": {}
            },
            'no-balance': {
                "label": 'No Open Balance',
                "filter": {"balance": 0}
            },
            'has-balance': {
                "label": 'Has an Open Balance',
                "filter": {"balance__gt": 0}
            }
        }.items()))
    },
    'invoice_status': {
        "label": "What Status",
        "options": OrderedDict(sorted({
            'all': {
                "label": 'All Statuses',
                "filter": {}
            },
            'no-balance': {
                "label": 'Only Estimates',
                "filter": {"status_detail__iexact": "estimate"}
            },
            'has-balance': {
                "label": 'Only Tendered',
                "filter": {"status_detail__iexact": "tendered"}
            }
        }.items()))
    }
}


class Report(TendenciBaseModel):
    """
        A Report represents a set of configurations for reporting
        on data from other models.
    """
    type = models.CharField(max_length=100)
    config = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')

    def __str__(self):
        return "%s %s " % (self.pk, str(self.type))

    def get_absolute_url(self):
        return reverse('report_detail', args=[self.pk])

    def runs(self):
        return Run.objects.filter(report=self).order_by('-create_dt')

    def config_options_dict(self):
        if self.config:
            return json.loads(self.config)
        return u''

    def config_options(self):
        if self.config:
            options = json.loads(self.config)
            output = []
            for opt_key, opt_val in options.items():
                if opt_key in CONFIG_OPTIONS:
                    config_option = CONFIG_OPTIONS[opt_key]
                    config_dict = {
                        'label': config_option['label'],
                        'value': config_option['options'][opt_val]['label']
                    }
                    output.append(config_dict)

                elif opt_key == "invoice_object_type":
                    value = ", ".join(sorted([get_ct_nice_name(i) for i in opt_val]))
                    if sorted(opt_val) == sorted([str(i['object_type']) for i in Invoice.objects.values('object_type').distinct()]):
                        value = "All Apps"
                    config_dict = {
                        'label': "Which Apps",
                        'value': value
                    }
                    output.append(config_dict)

                elif opt_key == "invoice_membership_filter":
                    try:
                        item = MembershipType.objects.get(pk=opt_val)
                        output.append({
                            'label': 'Membership Filter',
                            'value': '%s members only' % item.name
                        })
                    except:
                        pass

            return output
        return u''

    def config_options_string(self):
        if self.config_options():
            return '; '.join([i['value'] for i in self.config_options()])
        return u''

RUN_STATUS_CHOICES = (
    ('unstarted', 'Unstarted'),
    ('running', 'Running'),
    ('complete', 'Complete'),
    ('error', 'Error'),
)


RUN_TYPE_CHOICES = (
    ('html', 'HTML'),
    ('html-extended', 'HTML Extended'),
    ('html-summary', 'HTML Summary')
)


class Run(models.Model):
    """
        A Run tracks the start, end, and output of generating
        the results from a Report object.

        A Report can be 'run' multiple times with different
        range start and end times as well as output in different
        modes like HTML or PDF.
    """
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    create_dt = models.DateTimeField(auto_now_add=True)
    start_dt = models.DateTimeField(null=True)
    complete_dt = models.DateTimeField(null=True)
    range_start_dt = models.DateTimeField(null=True)
    range_end_dt = models.DateTimeField(null=True)
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=200, default="", blank=True)
    status = models.CharField(choices=RUN_STATUS_CHOICES, max_length=20, default="unstarted")
    output = models.TextField(blank=True)
    output_type = models.CharField(choices=RUN_TYPE_CHOICES, max_length=20, default="html")

    class Meta:
        verbose_name = _('Run')
        verbose_name_plural = _('Runs')

    def __str__(self):
        return "Run %s for report %s" % (self.pk, self.report.pk)

    def get_absolute_url(self):
        return reverse('report_run_detail', args=[self.report.pk, self.pk])

    def get_output_url(self):
        return reverse('report_run_output', args=[self.report.pk, self.pk])
