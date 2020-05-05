from builtins import str
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
import csv
import zipfile
from os import unlink
from time import time
from django.http import HttpResponse
from django.db.models.fields import DateTimeField, DateField, TimeField
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from celery.task import Task
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.exports.utils import render_csv

class TendenciExportTask(Task):
    """Export Task for Celery
    This exports the entire queryset of a given TendenciBaseModel.
    """

    def run(self, model, fields, file_name, **kwargs):
        """Create the xls file"""
        if issubclass(model, TendenciBaseModel):
            fields = fields + [
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

        items = model.objects.filter(status=True)
        start_dt = kwargs.get('start_dt', None)
        end_dt = kwargs.get('end_dt', None)
        include_files = kwargs.get('include_files', None)
        if start_dt and end_dt:
            if start_dt:
                try:
                    start_dt = datetime.strptime(start_dt, '%m/%d/%Y')
                except:
                    raise Exception('Please use the following date format MM/DD/YYYY.\n')
    
            if end_dt:
                try:
                    end_dt = datetime.strptime(end_dt, '%m/%d/%Y')
                    end_dt = end_dt + timedelta(days=1)
                except:
                    raise Exception('Please use the following date format MM/DD/YYYY.\n')
            if start_dt and end_dt:
                items = items.filter(update_dt__gte=start_dt, update_dt__lte=end_dt)
        data_row_list = []
        for item in items:
            # get the available fields from the model's meta
            opts = item._meta
            d = {}
            for f in opts.get_fields() + opts.many_to_many:
                if f.name in fields:  # include specified fields only
                    if isinstance(f, ManyToManyField):
                        value = ["%s" % obj for obj in f.value_from_object(item)]
                    elif isinstance(f, ForeignKey):
                        value = getattr(item, f.name)
                    elif isinstance(f, GenericRelation):
                        generics = f.value_from_object(item).all()
                        value = ["%s" % obj for obj in generics if obj !='']
                        value = ', '.join(value)
                    else:
                        value = f.value_from_object(item)
                        if value:
                            if isinstance(f, DateTimeField):
                                value = value.strftime("%Y-%m-%d %H:%M")
                            elif isinstance(f, DateField):
                                value = value.strftime("%Y-%m-%d")
                            elif isinstance(f, TimeField):
                                value = value.strftime('%H:%M:%S')

                    d[f.name] = value

            # append the accumulated values as a data row
            # keep in mind the ordering of the fields
            data_row = []
            for field in fields:
                # clean the derived values into unicode
                value = str(d[field]).rstrip()
                data_row.append(value)

            data_row_list.append(data_row)
            
        if include_files:
            if model._meta.model_name == 'resume':
                temp_csv = NamedTemporaryFile(mode='w', delete=False)
                csv_writer = csv.writer(temp_csv, delimiter=',')
                csv_writer.writerow(fields)
                for data_row in data_row_list:
                    csv_writer.writerow(data_row)
                temp_csv.close()
                
                temp_zip = NamedTemporaryFile(mode='wb', delete=False)
                zip_fp = zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED)
                # handle files
                for item in items:
                    if item.resume_file:
                        zip_fp.write(item.resume_file.path, item.resume_file.name, zipfile.ZIP_DEFLATED)
                zip_fp.write(temp_csv.name, 'resumes.csv', zipfile.ZIP_DEFLATED)
                zip_fp.close()
                temp_zip.close()
                
                # set the response for the zip files
                with open(temp_zip.name, 'rb') as f:
                    content = f.read()
            
                response = HttpResponse(content, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="export_resumes_%d.zip"' % time()
    
                # remove the temporary files
                unlink(temp_zip.name)
                unlink(temp_csv.name)
                
                return response
                
        return render_csv(file_name, fields, data_row_list)
