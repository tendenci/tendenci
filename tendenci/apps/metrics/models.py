from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


class Metric(models.Model):
    """
    Metrics for the sites usage
    """
    users = models.IntegerField(_('users'))
    members = models.IntegerField(_('members'))
    visits = models.IntegerField(_('visits'))
    disk_usage = models.BigIntegerField(_('disk usage'))
    invoices = models.IntegerField(_('invoices'), null=True)
    positive_invoices = models.IntegerField(_('invoices with a total that is not 0'), null=True)
    invoice_totals = models.DecimalField(_("sum of invoices' totals"), max_digits=12, decimal_places=2, null=True)
    create_dt = models.DateTimeField(_('create date/time'), auto_now_add=True)

    def __unicode__(self):
        return 'Metrics: %d' % self.pk

    def delta(self, value):
        if value > 0:
            css = "pos"
        elif value < 0:
            css = "neg"
        if value != 0:
            return mark_safe('<span class="%s">%s</span>' % (css, value))
        else:
            return '-'

    def users_delta(self):
        try:
            previous_users = Metric.objects.filter(create_dt__lt=self.create_dt).order_by('-create_dt')[0]
            return self.delta(int(self.users) - int(previous_users.users))
        except:
            pass

    def members_delta(self):
        try:
            previous_members = Metric.objects.filter(create_dt__lt=self.create_dt).order_by('-create_dt')[0]
            return self.delta(int(self.members) - int(previous_members.members))
        except:
            pass

    def visits_delta(self):
        try:
            previous_visits = Metric.objects.filter(create_dt__lt=self.create_dt).order_by('-create_dt')[0]
            return self.delta(int(self.visits) - int(previous_visits.visits))
        except:
            pass

    def disk_usage_delta(self):
        try:
            previous_disk_usage = Metric.objects.filter(create_dt__lt=self.create_dt).order_by('-create_dt')[0]
            return int(self.disk_usage) - int(previous_disk_usage.disk_usage)
        except:
            pass

    def disk_usage_css(self):
        try:
            previous_disk_usage = Metric.objects.filter(create_dt__lt=self.create_dt).order_by('-create_dt')[0]
            value = int(self.disk_usage) - int(previous_disk_usage.disk_usage)
            if value > 0:
                return "pos"
            elif value < 0:
                return "neg"
        except:
            pass
