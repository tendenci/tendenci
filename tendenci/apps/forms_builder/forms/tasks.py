from builtins import str
import os
import csv
import zipfile
from io import open
from os.path import join
from os import unlink
from time import time
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.db.models import Max, Count
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.template.defaultfilters import yesno
from django.core.files.storage import default_storage
import celery

from tendenci.apps.exports.utils import full_model_to_dict, render_csv
from tendenci.apps.forms_builder.forms.models import Form
from tendenci.apps.forms_builder.forms.utils import form_entries_to_csv_writer
from tendenci.apps.base.utils import escape_csv


class FormsExportTask(celery.Task):
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
            'allow_anonymous_view',
            'allow_user_view',
            'allow_member_view',
            'allow_user_edit',
            'allow_member_edit',
            'create_dt',
            'update_dt',
            'creator',
            'creator_username',
            'owner',
            'owner_username',
            'status',
            'status_detail',
        ]
        field_fields = [
            'label',
            'field_type',
            'field_function',
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

        forms = Form.objects.filter(status=True)
        max_fields = forms.annotate(num_fields=Count('fields')).aggregate(Max('num_fields'))['num_fields__max']
        max_pricings = forms.annotate(num_pricings=Count('pricing')).aggregate(Max('num_pricings'))['num_pricings__max']
        file_name = 'forms.csv'
        data_row_list = []

        for form in forms:
            data_row = []
            # form setup
            form_d = full_model_to_dict(form)
            for field in form_fields:
                if field == 'payment_methods':
                    value = [m.human_name for m in form.payment_methods.all()]
                else:
                    value = form_d[field]
                value = str(value).replace(os.linesep, ' ').rstrip()
                value = escape_csv(value)
                data_row.append(value)

            if form.fields.all():
                # field setup
                for field in form.fields.all():
                    field_d = full_model_to_dict(field)
                    for f in field_fields:
                        value = field_d[f]
                        value = str(value).replace(os.linesep, ' ').rstrip()
                        value = escape_csv(value)
                        data_row.append(value)

            # fill out the rest of the field columns
            if form.fields.all().count() < max_fields:
                for i in range(0, max_fields - form.fields.all().count()):
                    for f in field_fields:
                        data_row.append('')

            if form.pricing_set.all():
                # field setup
                for pricing in form.pricing_set.all():
                    pricing_d = full_model_to_dict(pricing)
                    for f in pricing_fields:
                        value = pricing_d[f]
                        value = str(value).replace(os.linesep, ' ').rstrip()
                        value = escape_csv(value)
                        data_row.append(value)

            # fill out the rest of the field columns
            if form.pricing_set.all().count() < max_pricings:
                for i in range(0, max_pricings - form.pricing_set.all().count()):
                    for f in pricing_fields:
                        data_row.append('')

            data_row_list.append(data_row)

        fields = form_fields
        for i in range(0, max_fields):
            fields = fields + ["field %s %s" % (i, f) for f in field_fields]
        for i in range(0, max_pricings):
            fields = fields + ["pricing %s %s" % (i, f) for f in pricing_fields]
        return render_csv(file_name, fields, data_row_list)


class FormEntriesExportTask(celery.Task):

    def run(self, form_instance, entries, include_files, **kwargs):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_entries_%d.csv"' % time()
        has_files = form_instance.has_files() and include_files

        # if the object hase file store the csv elsewhere
        # so that we can zip the files
        if has_files:
            temp_csv = NamedTemporaryFile(mode='w', delete=False)
            temp_zip = NamedTemporaryFile(mode='wb', delete=False)
            csv_writer = csv.writer(temp_csv, delimiter=',')
            zip = zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED)
        else:
            csv_writer = csv.writer(response, delimiter=',')
            
        form_entries_to_csv_writer(csv_writer, form_instance)

        # handle files
        for entry in entries:
            for field in entry.fields.all().order_by('field__position', 'id'):
                if has_files and field.field.field_type == 'FileField':
                    archive_name = join('files',field.value)
                    if hasattr(settings, 'USE_S3_STORAGE') and settings.USE_S3_STORAGE:
                        file_path = field.value
                        try:
                            # TODO: for large files, we may need to copy down
                            # the files before adding them to the zip file.
                            zip.writestr(archive_name, default_storage.open(file_path).read())
                        except IOError:
                            pass
                    else:
                        file_path = join(settings.MEDIA_ROOT,field.value)
                        zip.write(file_path, archive_name, zipfile.ZIP_DEFLATED)


        # add the csv file to the zip, close it, and set the response
        if has_files:
            # add the csv file and close it all out
            temp_csv.close()
            zip.write(temp_csv.name, 'entries.csv', zipfile.ZIP_DEFLATED)
            zip.close()
            temp_zip.close()

            # set the response for the zip files
            with open(temp_zip.name, 'rb') as f:
                body = f.read()
            response = HttpResponse(body, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="export_entries_%d.zip"' % time()

            # remove the temporary files
            unlink(temp_zip.name)
            unlink(temp_csv.name)

        return response
