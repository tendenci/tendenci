# -*- coding: utf-8 -*-
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.contrib.contenttypes.models import ContentType
from tendenci.apps.entities.models import Entity


OBJECT_TYPE_DICT = dict((ct.id, '%s: %s' % (ct.app_label, ct.name))
                        for ct in ContentType.objects.all())
DEFAULT_OBJ_TYPES = ('registration', 'membershipdefault',
                     'membershipset', 'makepayment',
                     'corpmembership', 'job')
ENTITY_DICT = dict((e.id, e.entity_name) for e in Entity.objects.all())


def base_label(report, field):
    if hasattr(field, 'verbose_name'):
        return "%s" % field.verbose_name.title()
    return field

base_lookup_label = lambda report, field: "[%s] %s" % (field.model._meta.verbose_name.title(), field.verbose_name.title())

model_lookup_label = lambda report, field: "[%s] %s" % (report.model._meta.verbose_name.title(), field.verbose_name.title())


def sum_column(values):
    if not values:
        return Decimal(0.00)
    if isinstance(values[0], (list, tuple)):
        return Decimal([v if str.isdigit(str(v[0] if isinstance(v, (list, tuple)) else v)) else 1 for v in values])
    return Decimal(sum(values))
sum_column.caption = _('Total')


def avg_column(values):
    if not values:
        return Decimal(0.00)
    return Decimal(float(sum_column(values)) / float(len(values)))
avg_column.caption = _('Average')


def count_column(values):
    return Decimal(len(values))
count_column.caption = _('Count')


def date_format(value, instance):
    return value.strftime("%d/%m/%Y")


def usd_format(value, instance):
    return 'USD %.2f' % Decimal(value)


def yesno_format(value, instance):
    return _('Yes') if value else _('No')


def round_format(value, instance):
    return Decimal('%.2f' % Decimal(value))


def us_date_format(value, instance):
    return value.strftime("%m/%d/%Y")


def date_label(report, field):
    return _("Date")


def obj_type_format(value, instance):
    return OBJECT_TYPE_DICT.get(value)


def entity_format(value):
    return '%s (Entity ID: %s)' % (ENTITY_DICT.get(value), value)


def date_from_datetime(value):
    return value.date()


def get_obj_type_choices():
    choices = ContentType.objects.filter(model__in=DEFAULT_OBJ_TYPES)
    return choices


class ReportValue(object):
    value = None
    is_report_total = False
    is_group_total = False
    is_value = True

    def __init__(self, value):
        self.value = value

    def format(self, value, instance):
        return value

    def text(self):
        return force_unicode(self.format(self.value, instance=self))

    def __repr__(self):
        return self.text()

    def __unicode__(self):
        return self.text()

    def __str__(self):
        return "%s" % self.text()

    def __iter__(self):
        return self.value.__iter__()


class ReportRow(list):
    is_total = False
    is_caption = False

    def get_css_class(self):
        classes = []
        if self.is_total:
            classes.append('total')
        if self.is_caption:
            classes.append('caption')
        return " ".join(classes)

    def is_value(self):
        return self.is_total == False and self.is_caption == False
