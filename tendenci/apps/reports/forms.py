from datetime import datetime

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

from tendenci.addons.memberships.models import MembershipType
from tendenci.apps.invoices.models import Invoice
from tendenci.core.perms.utils import update_perms_and_save
from tendenci.apps.reports.utils import get_ct_nice_name
from tendenci.apps.reports.models import Report, Run, REPORT_TYPE_CHOICES, CONFIG_OPTIONS


class ReportForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES)

    class Meta:
        model = Report

        fields = ["type"]

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)

        fields_to_append = ['invoice_display', 'invoice_status']

        for item in fields_to_append:
            self.fields[item] = forms.ChoiceField(choices=[
                (k, v['label']) for k, v in CONFIG_OPTIONS[item]['options'].items()],
                label=CONFIG_OPTIONS[item]['label'])

        if 'invoice_status' in self.fields:
            self.fields['invoice_status'].initial = 'has-balance'

        self.fields['invoice_membership_filter'] = forms.ChoiceField(
            label="Filter results based on membership type (if membership is selected)",
            choices=[('', '--- Membership type filter ---')] + sorted([(i['pk'], i['name']) for i in MembershipType.objects.values('pk', 'name')], key=lambda t: t[0]),
            required=False)

        self.fields['invoice_object_type'] = forms.MultipleChoiceField(
            label="Which apps to include?",
            choices=sorted([(i['object_type'], get_ct_nice_name(i['object_type'])) for i in Invoice.objects.values('object_type').distinct()], key=lambda t: t[1]),
            widget=forms.widgets.CheckboxSelectMultiple(),
            initial=[i['object_type'] for i in Invoice.objects.values('object_type').distinct()])

    def save(self, *args, **kwargs):
        request = kwargs.get('request')
        if request:
            del kwargs['request']
        report = super(ReportForm, self).save(*args, **kwargs)

        if request:
            update_perms_and_save(request, self, report)

        config_dict = {}
        if self.cleaned_data['type'] == "invoices":
            for k, v in self.cleaned_data.items():
                if "invoice" in k:
                    config_dict.update({k: v})

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
