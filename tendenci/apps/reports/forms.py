from datetime import datetime

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

from tendenci.core.perms.utils import update_perms_and_save
from tendenci.apps.reports.models import Report, Run, REPORT_TYPE_CHOICES, CONFIG_OPTIONS


class ReportForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES)

    class Meta:
        model = Report

        fields = ["type"]

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)

        fields_to_append = ['invoice_display']

        for item in fields_to_append:
            self.fields[item] = forms.ChoiceField(choices=[
                (k, v['label']) for k, v in CONFIG_OPTIONS[item]['options'].items()],
                label=CONFIG_OPTIONS[item]['label'])

    def save(self, *args, **kwargs):
        request = kwargs.get('request')
        if request:
            del kwargs['request']
        report = super(ReportForm, self).save(*args, **kwargs)

        if request:
            update_perms_and_save(request, self, report)

        config_dict = {}
        if "invoice_display" in self.cleaned_data:
            config_dict.update({'invoice_display': self.cleaned_data['invoice_display']})

        config_json = json.dumps(config_dict, cls=DjangoJSONEncoder)
        report.config = config_json
        report.allow_anonymous_view = False
        report.save()

        return report


class RunForm(forms.ModelForm):
    range_start_dt = forms.CharField(widget=forms.DateTimeInput(format='%m/%d/%Y'), label="Start Date", required=False)
    range_end_dt = forms.CharField(widget=forms.DateTimeInput(format='%m/%d/%Y'), label="End Date", required=False)

    class Meta:
        model = Run

        fields = [
            "report",
            "range_start_dt",
            "range_end_dt",
            "output_type"
        ]

    def clean_range_start_dt(self):
        range_start_dt = self.cleaned_data.get('range_start_dt')
        if range_start_dt:
            try:
                range_start_dt = datetime.strptime(range_start_dt, '%m/%d/%Y')
            except ValueError:
                range_start_dt = None
                self._errors['range_start_dt'] = ['Invalid date selected.']
        else:
            range_start_dt = None
        return range_start_dt

    def clean_range_end_dt(self):
        range_end_dt = self.cleaned_data.get('range_end_dt')
        if range_end_dt:
            try:
                range_end_dt = datetime.strptime(range_end_dt, '%m/%d/%Y')
            except ValueError:
                range_end_dt = None
                self._errors['range_end_dt'] = ['Invalid date selected.']
        else:
            range_end_dt = None
        return range_end_dt

    def save(self, *args, **kwargs):
        request = kwargs.get('request')
        if request:
            del kwargs['request']
        run = super(RunForm, self).save(*args, **kwargs)

        if request:
            run.creator = request.user
            run.creator_username = request.user.username
        run.save()

        return run
