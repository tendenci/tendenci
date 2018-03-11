# coding=utf-8
from builtins import str
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from tendenci.libs.model_report.widgets import RangeField


class ConfigForm(forms.Form):

    DEFAULT_CHART_TYPES = (
        ('area', _('Area')),
        ('line', _('Line')),
        ('column', _('Columns')),
        ('pie', _('Pie')),
    )
    CHART_SERIE_OPERATOR = (
        ('', '---------'),
        ('sum', _('Sum')),
        ('len', _('Count')),
        ('avg', _('Average')),
        ('min', _('Min')),
        ('max', _('Max')),
    )

    chart_mode = forms.ChoiceField(label=_('Chart type'), choices=(), required=False)
    serie_field = forms.ChoiceField(label=_('Serie field'), choices=(), required=False)
    serie_op = forms.ChoiceField(label=_('Serie operator'), choices=CHART_SERIE_OPERATOR, required=False)

    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        choices = [('', '')]
        for k, v in self.DEFAULT_CHART_TYPES:
            if k in self.chart_types:
                choices.append([k, v])
        self.fields['chart_mode'].choices = list(choices)
        choices = [('', '')]
        for i, (index, mfield, field, caption) in enumerate(self.serie_fields):
            choices += (
                (index, caption),
            )
        self.fields['serie_field'].choices = list(choices)

    def get_config_data(self):
        data = getattr(self, 'cleaned_data', {})
        if not data:
            return {}
        if not data['serie_field'] or not data['chart_mode'] or not data['serie_op']:
            return {}
        data['serie_field'] = int(data['serie_field'])
        return data


class GroupByForm(forms.Form):

    groupby = forms.ChoiceField(label=_('Group by field:'), required=False)
    onlytotals = forms.BooleanField(label=_('Show only totals'), required=False)

    def _post_clean(self):
        pass

    def __init__(self, **kwargs):
        super(GroupByForm, self).__init__(**kwargs)
        choices = [(None, '')]
        for i, (mfield, field, caption) in enumerate(self.groupby_fields):
            choices.append((field, caption))
        self.fields['groupby'].choices = choices
        data = kwargs.get('data', {})
        if data:
            self.fields['groupby'].initial = data.get('groupby', '')

    def get_cleaned_data(self):
        cleaned_data = getattr(self, 'cleaned_data', {})
        if 'groupby' in cleaned_data:
            if str(cleaned_data['groupby']) == u'None':
                cleaned_data['groupby'] = None
        return cleaned_data


class FilterForm(forms.BaseForm):

    def _post_clean(self):
        pass

    def get_filter_kwargs(self):
        if not self.is_valid():
            return {}
        filter_kwargs = dict(self.cleaned_data)
        for k, v in filter_kwargs.copy().items():
            if not v:
                filter_kwargs.pop(k)
                continue
            if k == '__all__':
                filter_kwargs.pop(k)
                continue
            if isinstance(v, (list, tuple)):
                if isinstance(self.fields[k], (RangeField)):
                    filter_kwargs.pop(k)
                    start_range, end_range = v
                    if start_range:
                        filter_kwargs['%s__gte' % k] = start_range
                    if end_range:
                        filter_kwargs['%s__lte' % k] = end_range
            elif hasattr(self.fields[k], 'as_boolean'):
                if v:
                    filter_kwargs.pop(k)
                    filter_kwargs[k] = (str(v) == u'True')
        return filter_kwargs

    def get_cleaned_data(self):
        return getattr(self, 'cleaned_data', {})

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.filter_report_is_all = '__all__' in self.fields and len(self.fields) == 1
        try:
            data_filters = {}
            vals = args[0]
            for k in vals:
                if k in self.fields:
                    data_filters[k] = vals[k]
            for name in self.fields:
                for k, v in data_filters.items():
                    if k == name:
                        continue
                    field = self.fields[name]
                    if hasattr(field, 'queryset'):
                        qs = field.queryset
                        model_field_names = [f.name for f in qs.model._meta.get_fields()
                                             if not (f.many_to_one and f.related_model is None)]
                        if k in model_field_names:
                            field.queryset = qs.filter(Q(**{k: v}))
        except:
            pass

        for field in self.fields:
            self.fields[field].required = False
