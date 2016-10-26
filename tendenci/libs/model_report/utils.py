# -*- coding: utf-8 -*-
from decimal import Decimal
from string import capwords
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.contrib.contenttypes.models import ContentType
from tendenci.apps.entities.models import Entity


OBJECT_TYPE_DICT = dict((ct.id, '%s: %s' % (ct.app_label, ct.model))
                        for ct in ContentType.objects.all().order_by('app_label', 'model'))
DEFAULT_OBJ_TYPES = ('registration', 'membershipdefault',
                     'membershipset', 'makepayment',
                     'corpmembership', 'job',
                     'donation')
ENTITY_DICT = dict((e.id, e.entity_name) for e in Entity.objects.all())

def base_label(report, field):
    """
    Basic label
    """
    if hasattr(field, 'verbose_name'):
        return "%s" % capwords(field.verbose_name)
    return field

base_lookup_label = lambda report, field: "[%s] %s" % (field.model._meta.verbose_name.title(), field.verbose_name.title())

model_lookup_label = lambda report, field: "[%s] %s" % (report.model._meta.verbose_name.title(), field.verbose_name.title())


def sum_column(values):
    """
    Sum values for any column
    """
    if not values:
        return Decimal(0.00)
    if isinstance(values[0], (list, tuple)):
        return Decimal(sum([v if str.isdigit(str(v[0] if isinstance(v, (list, tuple)) else v)) else 1 for v in values]))
    return Decimal(sum(values))
sum_column.caption = _('Total')


def avg_column(values):
    """
    Average values for any column
    """
    if not values:
        return Decimal(0.00)
    return Decimal(float(sum_column(values)) / float(len(values)))
avg_column.caption = _('Average')


def count_column(values):
    """
    Count values for any column
    """
    return Decimal(len(values))
count_column.caption = _('Count')


def date_format(value, instance):
    """
    Format cell value to friendly date string
    """
    return value.strftime("%d/%m/%Y")


def usd_format(value, instance):
    """
    Format cell value to money
    """
    return 'USD %.2f' % Decimal(value)


def yesno_format(value, instance):
    """
    Format boolean value to render Yes or No if True or False
    """
    return _('Yes') if value else _('No')


def round_format(value, instance):
    """
    Format value to render with 2 decimal places
    """
    return Decimal('%.2f' % Decimal(value))

def us_date_format(value, instance):
    if isinstance(value, datetime):
        return value.strftime("%m/%d/%Y")
    return value


def date_label(report, field):
    return _("Date")


def obj_type_format(value, instance=None):
    return OBJECT_TYPE_DICT.get(value)


def entity_format(value):
    return '%s (Entity ID: %s)' % (ENTITY_DICT.get(value), value)


def date_from_datetime(value):
    return value.date()


def get_obj_type_choices():
    choices = ContentType.objects.filter(model__in=DEFAULT_OBJ_TYPES)
    return choices

class ReportValue(object):
    """
    Class to represent cells values for report rows

    Attributes:

    * ``value`` - real value from database
    * ``is_report_total`` - defined as True if value is for showing in report total row
    * ``is_group_total`` - defined as True if value is for showing in group total row
    * ``is_value`` - defined as True if value is for showing in normal row
    """
    value = None
    is_report_total = False
    is_group_total = False
    is_value = True

    def __init__(self, value):
        self.value = value

    def format(self, value, instance):
        """
        Format the value instance.
        """
        return value

    def text(self):
        """
        Render as text the value. This function also format the value.
        """
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
    """
    Class to represent report rows

    Attributes:

    * ``is_total`` - defined as True if row is a group total row or report total row
    * ``is_caption`` - TODO
    """
    is_total = False
    is_caption = False

    def get_css_class(self):
        """
        Render css classes to this row into html representation
        """
        classes = []
        if self.is_total:
            classes.append('total')
        if self.is_caption:
            classes.append('caption')
        return " ".join(classes)

    def is_value(self):
        """
        Evaluate True if the row is a normal row or not
        """
        return self.is_total == False and self.is_caption == False
