import os
from django.forms.models import model_to_dict
from django.db.models import Avg, Max, Min, Count
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict
from celery.task import Task
from celery.registry import tasks
from imports.utils import render_excel
from forms_builder.forms.models import Form

class FormsExportTask(Task):
    """Export Task for Celery
    This exports all forms along with their fields.
    """
    
    def run(self, **kwargs):
        """Create the xls file"""
        form_fields = [
            'title',
            'slug',
            'intro',
            'response',
            'email_text',
            'subject_template',
            'send_email',
            'email_from',
            'email_copies',
            'completion_url',
            'custom_payment',
            'payment_methods',
        ]
        field_fields = [
            'label',
            'field_type',
            'field_function',
            'function_params',
            'required',
            'visible',
            'choices',
            'position',
            'default',
        ]
        pricing_fields = [
            'label',
            'price',
        ]
        
        forms = Form.objects.filter(status=1)
        max_fields = forms.annotate(num_fields=Count('fields')).aggregate(Max('num_fields'))['num_fields__max']
        max_pricings = forms.annotate(num_pricings=Count('pricing')).aggregate(Max('num_pricings'))['num_pricings__max']
        file_name = 'forms.xls'
        data_row_list = []
        
        for form in forms:
            data_row = []
            # form setup
            form_d = model_to_dict(form)
            for field in form_fields:
                if field == 'payment_methods':
                    value = [m.human_name for m in form.payment_methods.all()]
                else:
                    value = form_d[field]
                value = unicode(value).replace(os.linesep, ' ').rstrip()
                data_row.append(value)
                
            if form.fields.all():
                # field setup
                for field in form.fields.all():
                    field_d = model_to_dict(field)
                    for f in field_fields:
                        value = field_d[f]
                        value = unicode(value).replace(os.linesep, ' ').rstrip()
                        data_row.append(value)
            
            # fill out the rest of the field columns
            if form.fields.all().count() < max_fields:
                for i in range(0, max_fields - form.fields.all().count()):
                    for f in field_fields:
                        data_row.append('')
                        
            if form.pricing_set.all():
                # field setup
                for pricing in form.pricing_set.all():
                    pricing_d = model_to_dict(pricing)
                    for f in pricing_fields:
                        value = pricing_d[f]
                        value = unicode(value).replace(os.linesep, ' ').rstrip()
                        data_row.append(value)
            
            # fill out the rest of the field columns
            if form.pricing_set.all().count() < max_pricings:
                for i in range(0, max_pricings - form.pricing_set.all().count()):
                    for f in pricing_fields:
                        data_row.append('')
            
            data_row.append('\n') # append a new line to make a new row
            data_row_list.append(data_row)
        
        fields = form_fields
        for i in range(0, max_fields):
            fields = fields + ["field %s %s" % (i, f) for f in field_fields]
        for i in range(0, max_pricings):
            fields = fields + ["pricing %s %s" % (i, f) for f in pricing_fields]
        fields.append('\n')
        return render_excel(file_name, fields, data_row_list)
