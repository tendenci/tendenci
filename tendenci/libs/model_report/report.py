# -*- coding: utf-8 -*-
import copy
from xlwt import Workbook, easyxf
from itertools import groupby

import django
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import DateTimeField, DateField
from django.utils.encoding import force_unicode
from django.db.models import Q
from django import forms
from django.forms.models import fields_for_model
try:
    from django.db.models.fields.related import ForeignObjectRel
except ImportError:  # Django < 1.8
    from django.db.models.related import RelatedObject as ForeignObjectRel
from django.db.models import ForeignKey
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import MultipleChoiceField
from django.forms.widgets import SelectMultiple

from tendenci.libs.model_report.exporters.excel import ExcelExporter
from tendenci.libs.model_report.exporters.pdf import PdfExporter
from tendenci.libs.model_report.forms import ConfigForm, GroupByForm, FilterForm
from tendenci.libs.model_report.utils import base_label, ReportValue, ReportRow, get_obj_type_choices
from tendenci.libs.model_report.highcharts import HighchartRender
from tendenci.libs.model_report.widgets import RangeField


try:
    from collections import OrderedDict
except:
    OrderedDict = dict  # pyflakes:ignore


def autodiscover(module_name='reports.py'):
    """
    Auto-discover INSTALLED_APPS report.py modules and fail silently when
    not present. Borrowed form django.contrib.admin
    """

    from importlib import import_module
    from django.utils.module_loading import module_has_submodule

    global reports

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(reports)
            import_module('%s.%s' % (app, module_name))
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            reports = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, module_name):
                raise


class ReportClassManager(object):
    """
    Class to handle registered reports class.
    """

    _register = OrderedDict()

    def __init__(self):
        self._register = OrderedDict()

    def register(self, slug, rclass):
        if slug in self._register:
            raise ValueError('Slug already exists: %s' % slug)
        setattr(rclass, 'slug', slug)
        self._register[slug] = rclass

    def get_report(self, slug):
        # return class
        return self._register.get(slug, None)

    def get_reports(self):
        # return clasess
        return self._register.values()


reports = ReportClassManager()


_cache_class = {}


def cache_return(fun):
    """
    Usages of this decorator have been removed from the ReportAdmin base class.

    Caching method returns gets in the way of customization at the implementation level
    now that report instances can be modified based on request data.
    """
    def wrap(self, *args, **kwargs):
        cache_field = '%s_%s' % (self.__class__.__name__, fun.func_name)
        if cache_field in _cache_class:
            return _cache_class[cache_field]
        result = fun(self, *args, **kwargs)
        _cache_class[cache_field] = result
        return result
    return wrap


def is_date_field(field):
    """ Returns True if field is DateField or DateTimeField,
    otherwise False """
    return isinstance(field, DateField) or isinstance(field, DateTimeField)


def get_model_name(model):
    """ Returns string name for the given model """
    # model._meta.module_name is deprecated in django version 1.7 and removed in django version 1.8.
    if django.VERSION < (1, 7):
        return model._meta.module_name
    else:
        return model._meta.model_name


class ReportAdmin(object):
    """
    Class to represent a Report.
    """

    fields = []
    """List of fields or lookup fields for query results to be listed."""

    model = None
    """Primary django model to query."""

    list_filter = ()
    """List of fields or lookup fields to filter data."""

    list_filter_widget = {}
    """Widget for list filter field"""

    list_filter_queryset = {}
    """ForeignKey custom queryset"""

    list_order_by = ()
    """List of fields or lookup fields to order data."""

    list_group_by = ()
    """List of fields or lookup fields to group data."""

    list_serie_fields = ()
    """List of fields to group by results in chart."""

    base_template_name = 'base.html'
    """Template file name to render the report."""

    template_name = 'model_report/report.html'
    """Template file name to render the report."""

    title = None
    """Title of the report."""

    type = 'report'
    """"report" for only report and  "chart" for report and chart graphic results."""

    group_totals = {}
    """Dictionary with field name as key and function to calculate their values."""

    report_totals = {}
    """Dictionary with field name as key and function to calculate their values."""

    override_field_values = {}
    """
    Dictionary with field name as key and function to parse their original values.

    ::

        override_field_values = {
            'men': men_format,
            'women': women_format
        }
    """
    override_field_formats = {}
    """Dictionary with field name as key and function to parse their value after :func:`override_field_values`."""

    override_field_labels = {}
    """Dictionary with field name as key and function to parse the column label."""

    override_field_choices = {}
    """#TODO"""

    override_field_filter_values = {}
    """#TODO"""

    override_group_value = {}
    """#TODO"""

    chart_types = ()
    """List of highchart types."""

    exporters = {
        'excel': ExcelExporter,
        'pdf': PdfExporter
    }

    exports = ('excel', 'pdf')
    """Alternative render report as "pdf" or "csv"."""

    inlines = []
    """List of other's Report related to the main report."""

    query_set = None
    """#TODO"""

    extra_fields = {}
    """ Dictionary of fields that are aggregated to the query.
    Format {field_name: Field instance}"""

    always_show_full_username = False

    def __init__(self, parent_report=None, request=None):
        self.parent_report = parent_report
        self.request = request
        model_fields = []
        model_m2m_fields = []
        self.related_inline_field = None
        self.related_inline_accessor = None
        self.related_fields = []
        for field in self.get_query_field_names():
            try:
                m2mfields = []
                if '__' in field:
                    pre_field = None
                    base_model = self.model
                    for field_lookup in field.split("__"):
                        if not pre_field:
                            pre_field, _, _, is_m2m = base_model._meta.get_field_by_name(field_lookup)
                            if is_m2m:
                                m2mfields.append(pre_field)
                        elif isinstance(pre_field, ForeignObjectRel):
                            base_model = pre_field.model
                            pre_field = base_model._meta.get_field_by_name(field_lookup)[0]
                        else:
                            if is_date_field(pre_field):
                                pre_field = pre_field
                            else:
                                base_model = pre_field.rel.to
                                pre_field = base_model._meta.get_field_by_name(field_lookup)[0]
                    model_field = pre_field
                else:
                    if field in self.extra_fields:
                        model_field = self.extra_fields[field]
                    elif not 'self.' in field:
                        model_field = self.model._meta.get_field_by_name(field)[0]
                    else:
                        get_attr = lambda s: getattr(s, field.split(".")[1])
                        get_attr.verbose_name = field
                        model_field = field
            except IndexError:
                raise ValueError('The field "%s" does not exist in model "%s".' % (field, get_model_name(self.model)))
            model_fields.append([model_field, field])
            if m2mfields:
                model_m2m_fields.append([model_field, field, len(model_fields) - 1, m2mfields])
        self.model_fields = model_fields
        self.model_m2m_fields = model_m2m_fields
        if parent_report:
            self.related_inline_field = [f for f, x in self.model._meta.get_fields_with_model() if f.rel and hasattr(f.rel, 'to') and f.rel.to is self.parent_report.model][0]
            self.related_inline_accessor = self.related_inline_field.related.get_accessor_name()
            self.related_fields = ["%s__%s" % (get_model_name(pfield.model), attname) for pfield, attname in self.parent_report.model_fields if not isinstance(pfield, (str, unicode)) and  pfield.model == self.related_inline_field.rel.to]
            self.related_inline_filters = []

            for pfield, pattname in self.parent_report.model_fields:
                for cfield, cattname in self.model_fields:
                    try:
                        if pattname in cattname:
                            if pfield.model == cfield.model:
                                self.related_inline_filters.append([pattname, cattname, self.parent_report.get_fields().index(pattname)])
                    except Exception, e:
                        pass


    def _get_grouper_text(self, groupby_field, value):
        try:
            model_field = [mfield for mfield, field in self.model_fields if field == groupby_field][0]
        except:
            model_field = None
        value = self.get_grouper_text(value, groupby_field, model_field)
        if value is None or unicode(value) == u'None':
            if groupby_field is None or unicode(groupby_field) == u'None':
                value = force_unicode(_('Results'))
            else:
                value = force_unicode(_('Nothing'))
        return value

    def _get_value_text(self, index, value):
        try:
            model_field = self.model_fields[index][0]
        except:
            model_field = None

        value = self.get_value_text(value, index, model_field)
        if value is None or unicode(value) == u'None':
            value = ''
        if value == [None]:
            value = []
        return value

    def get_grouper_text(self, value, field, model_field):
        try:
            if not isinstance(model_field, (str, unicode)):
                obj = model_field.model(**{field: value})
                if hasattr(obj, 'get_%s_display' % field):
                    value = getattr(obj, 'get_%s_display' % field)()
        except:
            pass
        return value

    # @cache_return
    def get_m2m_field_names(self):
        return [field for ffield, field, index, mfield in self.model_m2m_fields]

    def get_value_text(self, value, index, model_field):
        try:
            if not isinstance(model_field, (str, unicode)):
                obj = model_field.model(**{model_field.name: value})
                if hasattr(obj, 'get_%s_display' % model_field.name):
                    return getattr(obj, 'get_%s_display' % model_field.name)()
        except:
            pass
        return value

    def get_empty_row_asdict(self, collection, default_value=[]):
        erow = {}
        for field in collection:
            erow[field] = copy.copy(default_value)
        return dict(copy.deepcopy(erow))

    def reorder_dictrow(self, dictrow):
        return [dictrow[field_name] for field_name in self.get_fields()]

    def get_fields(self):
        return [x for x in self.fields if not x in self.related_fields]

    def get_column_names(self, ignore_columns={}):
        """
        Return the list of columns
        """
        values = []
        for field, field_name in self.model_fields:
            if field_name in ignore_columns:
                continue
            caption = self.override_field_labels.get(field_name, base_label)
            if hasattr(caption, '__call__'):  # Is callable
                caption = caption(self, field)
            values.append(caption)
        return values

    # @cache_return
    def get_query_field_names(self):
        values = []
        for field in self.get_fields():
            if not 'self.' in field:
                values.append(field.split(".")[0])
            else:
                values.append(field)
        return values

    # @cache_return
    def get_query_set(self, filter_kwargs):
        """
        Return the the queryset
        """
        # Filter out invoices based on hardcoded object types specified
        if self.model._meta.verbose_name == 'invoice':
            try:
                qs = self.model.objects.filter(object_type__in=get_obj_type_choices())
            except Exception:
                qs = self.model.objects.all()
        else:
            qs = self.model.objects.all()
        for selected_field, field_value in filter_kwargs.items():
            if not field_value is None and field_value != '':
                if hasattr(field_value, 'values_list'):
                    field_value = field_value.values_list('pk', flat=True)
                    selected_field = '%s__pk__in' % selected_field.split("__")[0]
                elif isinstance(field_value, list):
                    if len(field_value) > 1:
                        selected_field = '%s__in' % selected_field
                    elif len(field_value) == 1:
                        if field_value[0] == '':
                            choices = []
                            for field in self.model_fields:
                                if field[1] == selected_field:
                                    for c in field[0].choices:
                                        choices.append(c[0])
                            field_value = choices
                            selected_field = '%s__in' % selected_field
                        else:
                            field_value = field_value[0]
                    else:
                        pass
                qs = qs.filter(Q(**{selected_field: field_value}))
        self.query_set = qs.distinct()
        return self.query_set

    def get_title(self):
        """
        Return the report title
        """
        title = self.title or None
        if not title:
            if not self.model:
                title = _('Unnamed report')
            else:
                title = force_unicode(self.model._meta.verbose_name_plural).lower().capitalize()
        return title

    def get_render_context(self, request, extra_context={}, by_row=None):
        context_request = request or self.request
        filter_related_fields = {}
        if self.parent_report and by_row:
            for mfield, cfield, index in self.related_inline_filters:
                filter_related_fields[cfield] = by_row[index].value

        try:
            form_groupby = self.get_form_groupby(context_request)
            form_filter = self.get_form_filter(context_request)
            form_config = self.get_form_config(context_request)

            column_labels = self.get_column_names(filter_related_fields)
            report_rows = []
            report_anchors = []
            chart = None

            if context_request.GET:
                groupby_data = form_groupby.get_cleaned_data() if form_groupby else None
                filter_kwargs = filter_related_fields or form_filter.get_filter_kwargs()
                if groupby_data:
                    self.__dict__.update(groupby_data)
                else:
                    self.__dict__['onlytotals'] = False

                report_rows = self.get_rows(groupby_data, filter_kwargs, filter_related_fields)

                for g, r in report_rows:
                    report_anchors.append(g)

                if len(report_anchors) <= 1:
                    report_anchors = []

                if self.type == 'chart' and groupby_data and groupby_data['groupby']:
                    config = form_config.get_config_data()
                    if config:
                        chart = self.get_chart(config, report_rows)

                if self.onlytotals:
                    for g, rows in report_rows:
                        for r in list(rows):
                            if r.is_value():
                                rows.remove(r)

                if not context_request.GET.get('export', None) is None and not self.parent_report:
                    exporter_class = self.exporters.get(context_request.GET.get('export'), None)
                    if exporter_class:
                        report_inlines = [ir(self, context_request) for ir in self.inlines]
                        return exporter_class.render(self, column_labels, report_rows, report_inlines)

            inlines = [ir(self, context_request) for ir in self.inlines]

            is_inline = self.parent_report is None
            render_report = not (len(report_rows) == 0 and is_inline)
            self.base_template_name = 'base-wide.html'
            print_view = request.GET.get('print', False)
            if print_view:
                self.base_template_name = 'base-print.html'
            context = {
                'render_report': render_report,
                'is_inline': is_inline,
                'inline_column_span': 0 if is_inline else len(self.parent_report.get_column_names()),
                'report': self,
                'form_groupby': form_groupby,
                'form_filter': form_filter,
                'form_config': form_config if self.type == 'chart' else None,
                'chart': chart,
                'report_anchors': report_anchors,
                'column_labels': column_labels,
                'report_rows': report_rows,
                'report_inlines': inlines,
                'base_template_name': self.base_template_name,
            }

            if extra_context:
                context.update(extra_context)

            context['request'] = request
            return context
        finally:
            globals()['_cache_class'] = {}

    def check_permissions(self, request):
        """ Override this method to another one raising Forbidden
        exceptions if you want to limit the access to the report """


    def render(self, request, extra_context={}):
        context_or_response = self.get_render_context(request, extra_context)
        self.check_permissions(request)

        if isinstance(context_or_response, HttpResponse):
            return context_or_response
        return render_to_response(self.template_name, context_or_response,
                                  context_instance=RequestContext(request))

    def has_report_totals(self):
        return not (not self.report_totals)

    def has_group_totals(self):
        return not (not self.group_totals)

    def get_chart(self, config, report_rows):
        config['title'] = self.get_title()
        config['has_report_totals'] = self.has_report_totals()
        config['has_group_totals'] = self.has_group_totals()
        return HighchartRender(config).get_chart(report_rows)

    def get_form_config(self, request):
        ConfigForm.serie_fields = self.get_serie_fields()
        ConfigForm.chart_types = self.chart_types
        form = ConfigForm(data=request.GET or None)
        form.is_valid()
        return form

    def get_groupby_fields(self):
        return [(mfield, field, caption) for (mfield, field), caption in zip(self.model_fields, self.get_column_names()) if field in self.list_group_by]

    def get_serie_fields(self):
        return [(index, mfield, field, caption) for index, ((mfield, field), caption) in enumerate(zip(self.model_fields, self.get_column_names())) if field in self.list_serie_fields]

    def get_form_groupby(self, request):
        groupby_fields = self.get_groupby_fields()

        if not groupby_fields:
            return None

        GroupByForm.groupby_fields = groupby_fields
        form = GroupByForm(data=request.GET or None)
        form.is_valid()
        return form

    def get_user_label(self, user):
        name = user.get_full_name()
        username = user.username
        return (name and name != username and '%s (%s)' % (name, username)
                or username)

    def check_for_widget(self, widget, field):
        if widget:
            for field_to_set_widget, widget in widget.iteritems():
                if field_to_set_widget == field:
                    return (True, widget, MultipleChoiceField().__class__)


    def get_form_filter(self, request):
        form_fields = fields_for_model(self.model, [f for f in self.get_query_field_names() if f in self.list_filter])
        if not form_fields:
            form_fields = {
                '__all__': forms.BooleanField(label='', widget=forms.HiddenInput, initial='1')
            }
        else:
            opts = self.model._meta
            for k, v in dict(form_fields).items():
                if v is None:
                    pre_field = None
                    base_model = self.model
                    if '__' in k:
                        # for field_lookup in k.split("__")[:-1]:
                        for field_lookup in k.split("__"):
                            if pre_field:
                                if isinstance(pre_field, ForeignObjectRel):
                                    base_model = pre_field.model
                                else:
                                    base_model = pre_field.rel.to
                            pre_field = base_model._meta.get_field_by_name(field_lookup)[0]

                        model_field = pre_field
                    else:
                        field_name = k.split("__")[0]
                        model_field = opts.get_field_by_name(field_name)[0]

                    if isinstance(model_field, (DateField, DateTimeField)):
                        form_fields.pop(k)
                        field = RangeField(model_field.formfield)
                    else:
                        if not hasattr(model_field, 'formfield'):
                            field = forms.ModelChoiceField(queryset=model_field.model.objects.all())
                            field.label = self.override_field_labels.get(k, base_label)(self, field) if k in self.override_field_labels else field_lookup

                        elif isinstance(model_field, ForeignKey):
                            field = model_field.formfield()

                            if self.always_show_full_username and (model_field.rel.to == User):
                                field.label_from_instance = self.get_user_label

                            if self.list_filter_queryset:
                                for query_field, query in self.list_filter_queryset.iteritems():
                                    if query_field == k:
                                        for variable, value in query.iteritems():
                                            field.queryset = field.queryset.filter(**{variable: value})

                        else:
                            field = model_field.formfield()
                            if self.list_filter_widget.has_key(k):
                                use_widget, widget, field_class = self.check_for_widget(self.list_filter_widget, k)
                                if use_widget:
                                    field.__class__ = field_class
                                    field.widget = widget
                                    field.choices = model_field.choices
                                    field.choices.insert(0, ('', '---------'))
                                    field.initial = ''

                        field.label = force_unicode(_(field.label))

                else:
                    if isinstance(v, (forms.BooleanField)):
                        form_fields.pop(k)
                        field = forms.ChoiceField()
                        field.label = v.label
                        field.help_text = v.help_text
                        field.choices = (
                            ('', ''),
                            (True, _('Yes')),
                            (False, _('No')),
                        )
                        setattr(field, 'as_boolean', True)
                    elif isinstance(v, (forms.DateField, forms.DateTimeField)):
                        field_name = k.split("__")[0]
                        model_field = opts.get_field_by_name(field_name)[0]
                        form_fields.pop(k)
                        field = RangeField(model_field.formfield)
                    # Change filter form fields specific to invoice reports
                    elif opts.verbose_name == 'invoice':
                        if k == 'status_detail':
                            form_fields.pop(k)
                            field = forms.ChoiceField()
                            field.label = v.label
                            field.help_text = v.help_text
                            field.choices = (
                                ('', _('All')),
                                ('estimate', _('Estimate')),
                                ('tendered', _('Tendered')),
                            )
                            field.initial = 'tendered'
                        elif k == 'object_type':
                            form_fields.pop(k)
                            field = forms.ModelChoiceField(queryset=get_obj_type_choices())
                            field.label = v.label
                            field.help_text = v.help_text
                    else:
                        field = v

                    if hasattr(field, 'choices'):
                        if not hasattr(field, 'queryset'):
                            if field.choices[0][0]:
                                field.choices.insert(0, ('', '---------'))
                                field.initial = ''

                # Provide a hook for updating the queryset
                if hasattr(field, 'queryset') and k in self.override_field_choices:
                    field.queryset = self.override_field_choices.get(k)(self, field.queryset)
                form_fields[k] = field

        FilterFormClass = type('FilterFormBase', (FilterForm,), {'base_fields': form_fields})
        form = FilterFormClass(data=request.GET or None)
        form.is_valid()
        return form

    def filter_query(self, qs):
        return qs

    def get_with_dotvalues(self, resources):
        # {1: 'field.method'}
        dot_indexes = dict([(index, dot_field) for index, dot_field in enumerate(self.get_fields()) if '.' in dot_field])
        dot_indexes_values = {}

        dot_model_fields = [(index, model_field[0]) for index, model_field in enumerate(self.model_fields) if index in dot_indexes]
        # [ 1, model_field] ]
        for index, model_field in dot_model_fields:
            model_ids = set([row[index] for row in resources])
            if isinstance(model_field, (unicode, str)) and 'self.' in model_field:
                model_qs = self.model.objects.filter(pk__in=model_ids)
            else:
                model_qs = model_field.rel.to.objects.filter(pk__in=model_ids)
            div = {}
            method_name = dot_indexes[index].split('.')[1]
            for obj in model_qs:
                method_value = getattr(obj, method_name)
                if callable(method_value):
                    method_value = method_value()
                div[obj.pk] = method_value
            dot_indexes_values[index] = div
            del model_qs

        if dot_indexes_values:
            new_resources = []
            for index_row, old_row in enumerate(resources):
                new_row = []
                for index, actual_value in enumerate(old_row):
                    if index in dot_indexes_values:
                        new_value = dot_indexes_values[index][actual_value]
                    else:
                        new_value = actual_value
                    new_row.append(new_value)
                new_resources.append(new_row)
            resources = new_resources
        return resources

    def compute_row_totals(self, row_config, row_values, is_group_total=False, is_report_total=False):
        total_row = self.get_empty_row_asdict(self.get_fields(), ReportValue(' '))
        for field in self.get_fields():
            if field in row_config:
                fun = row_config[field]
                value = fun(row_values[field])
                if field in self.get_m2m_field_names():
                    value = ReportValue([value, ])
                value = ReportValue(value)
                value.is_value = False
                value.is_group_total = is_group_total
                value.is_report_total = is_report_total
                # TODO: method should do only one thing.
                # Remove ovveride_field_values from this function.
                if field in self.override_field_values:
                    value.to_value = self.override_field_values[field]
                if field in self.override_field_formats:
                    value.format = self.override_field_formats[field]
                value.is_m2m_value = (field in self.get_m2m_field_names())
                total_row[field] = value
        row = self.reorder_dictrow(total_row)
        row = ReportRow(row)
        row.is_total = True
        return row

    def group_m2m_field_values(self, gqs_values):
        values_results = []
        m2m_indexes = [index for ffield, lkfield, index, field in self.model_m2m_fields]

        def get_key_values(gqs_vals):
            return [v if index not in m2m_indexes else None for index, v in enumerate(gqs_vals)]

        # gqs_values needs to already be sorted on the same key function
        # for groupby to work properly
        gqs_values.sort(key=get_key_values)
        res = groupby(gqs_values, key=get_key_values)
        for key, values in res:
            row_values = dict([(index, []) for index in m2m_indexes])
            for v in values:
                for index in m2m_indexes:
                    if v[index] not in row_values[index]:
                        row_values[index].append(v[index])
            for index, vals in row_values.items():
                key[index] = vals
            values_results.append(key)
        return values_results

    def compute_row_header(self, row_config):
        header_row = self.get_empty_row_asdict(self.get_fields(), ReportValue(''))
        for report_total_field, fun in row_config.items():
            if hasattr(fun, 'caption'):
                value = force_unicode(fun.caption)
            else:
                value = '&nbsp;'
            header_row[report_total_field] = value
        row = self.reorder_dictrow(header_row)
        row = ReportRow(row)
        row.is_caption = True
        return row

    def get_field_value(self, obj, field):
        if isinstance(obj, (dict)):
            return obj[field]
        left_field = field.split("__")[0]
        try:
            right_field = "__".join(field.split("__")[1:])
        except:
            right_field = ''
        if right_field:
            return self.get_field_value(getattr(obj, left_field), right_field)
        if hasattr(obj, 'get_%s_display' % left_field):
            attr = getattr(obj, 'get_%s_display' % field)
        else:
            attr = getattr(obj, field)
        if callable(attr):
            attr = attr()
        return attr

    def get_rows(self, groupby_data=None, filter_kwargs={}, filter_related_fields={}):
        report_rows = []

        for selected_field, field_value in filter_kwargs.items():
            if selected_field in self.override_field_filter_values:
                filter_kwargs[selected_field] = self.override_field_filter_values.get(selected_field)(self, field_value)

        qs = self.get_query_set(filter_kwargs)
        ffields = [f if 'self.' not in f else 'pk' for f in self.get_query_field_names() if f not in filter_related_fields]
        ffields_include_self = [f for f in self.get_query_field_names() if f not in filter_related_fields]
        extra_ffield = []
        backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]
        for f in list(ffields):
            if '__' in f:
                for field, name in self.model_fields:
                    if name == f:
                        if is_date_field(field):
                            fname, flookup = f.rsplit('__', 1)
                            fname = fname.split('__')[-1]
                            if not flookup in ('year', 'month', 'day'):
                                break
                            if flookup == 'year':
                                if 'sqlite' in backend:
                                    extra_ffield.append([f, "strftime('%%Y', " + fname + ")"])
                                elif 'postgres' in backend:
                                    extra_ffield.append([f, "cast(extract(year from " + fname + ") as integer)"])
                                elif 'mysql' in backend:
                                    extra_ffield.append([f, "YEAR(" + fname + ")"])
                                else:
                                    raise NotImplemented  # mysql
                            if flookup == 'month':
                                if 'sqlite' in backend:
                                    extra_ffield.append([f, "strftime('%%m', " + fname + ")"])
                                elif 'postgres' in backend:
                                    extra_ffield.append([f, "cast(extract(month from " + fname + ") as integer)"])
                                elif 'mysql' in backend:
                                    extra_ffield.append([f, "MONTH(" + fname + ")"])
                                else:
                                    raise NotImplemented  # mysql
                            if flookup == 'day':
                                if 'sqlite' in backend:
                                    extra_ffield.append([f, "strftime('%%d', " + fname + ")"])
                                elif 'postgres' in backend:
                                    extra_ffield.append([f, "cast(extract(day from " + fname + ") as integer)"])
                                elif 'mysql' in backend:
                                    extra_ffield.append([f, "DAY(" + fname + ")"])
                                else:
                                    raise NotImplemented  # mysql
                        break
        obfields = list(self.list_order_by)
        if groupby_data and groupby_data['groupby']:
            if groupby_data['groupby'] in obfields:
                obfields.remove(groupby_data['groupby'])
            obfields.insert(0, groupby_data['groupby'])
        qs = self.filter_query(qs)
        qs = qs.order_by(*obfields)
        if extra_ffield:
            qs = qs.extra(select=dict(extra_ffield))
        qs = qs.values_list(*ffields)
        qs_list = list(qs)

        qs_list = self.get_with_dotvalues(qs_list)
        if self.model_m2m_fields:
            qs_list = self.group_m2m_field_values(qs_list)

        if groupby_data and groupby_data['groupby']:
            groupby_field = groupby_data['groupby']
            if groupby_field in self.override_group_value:
                transform_fn = self.override_group_value.get(groupby_field)
                groupby_fn = lambda x: transform_fn(x[ffields.index(groupby_field)])
            else:
                groupby_fn = lambda x: x[ffields.index(groupby_field)]
        else:
            groupby_fn = lambda x: None

        qs_list.sort(key=groupby_fn)
        g = groupby(qs_list, key=groupby_fn)

        row_report_totals = self.get_empty_row_asdict(self.report_totals, [])
        for grouper, resources in g:
            rows = list()
            row_group_totals = self.get_empty_row_asdict(self.group_totals, [])
            for resource in resources:
                row = ReportRow()
                if isinstance(resource, (tuple, list)):
                    for index, value in enumerate(resource):
                        if ffields_include_self[index] in self.group_totals:
                            row_group_totals[ffields_include_self[index]].append(value)
                        elif ffields[index] in self.group_totals:
                            row_group_totals[ffields[index]].append(value)
                        elif ffields[index] in self.report_totals:
                            row_report_totals[ffields[index]].append(value)
                        value = self._get_value_text(index, value)
                        value = ReportValue(value)
                        if ffields[index] in self.override_field_values:
                            value.to_value = self.override_field_values[ffields[index]]
                        if ffields[index] in self.override_field_formats:
                            value.format = self.override_field_formats[ffields[index]]
                        row.append(value)
                else:
                    for index, column in enumerate(ffields):
                        value = self.get_field_value(resource, column)
                        if ffields[index] in self.group_totals:
                            row_group_totals[ffields[index]].append(value)
                        elif ffields[index] in self.report_totals:
                            row_report_totals[ffields[index]].append(value)
                        value = self._get_value_text(index, value)
                        value = ReportValue(value)
                        if column in self.override_field_values:
                            value.to_value = self.override_field_values[column]
                        if column in self.override_field_formats:
                            value.format = self.override_field_formats[column]
                        row.append(value)
                rows.append(row)
            if row_group_totals:
                if groupby_data['groupby']:
                    header_group_total = self.compute_row_header(self.group_totals)
                    row = self.compute_row_totals(self.group_totals, row_group_totals, is_group_total=True)
                    rows.append(header_group_total)
                    rows.append(row)
                for k, v in row_group_totals.items():
                    if k in row_report_totals:
                        row_report_totals[k].extend(v)

            if groupby_data and groupby_data['groupby']:
                grouper = self._get_grouper_text(groupby_data['groupby'], grouper)
            else:
                grouper = None
            if isinstance(grouper, (list, tuple)):
                grouper = grouper[0]
            report_rows.append([grouper, rows])
        if self.has_report_totals():
            header_report_total = self.compute_row_header(self.report_totals)
            row = self.compute_row_totals(self.report_totals, row_report_totals, is_report_total=True)
            header_report_total.is_report_totals = True
            row.is_report_totals = True
            report_rows.append([_('Totals'), [header_report_total, row]])

        return report_rows
