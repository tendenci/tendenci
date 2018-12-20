from builtins import str
import subprocess
import datetime
import csv
from django.http import HttpResponse
from django.conf import settings
from tendenci.libs.utils import python_executable
from tendenci.apps.exports.models import Export


def full_model_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dictionay for an intance's model fields.
    Unlike django's model_to_dict this returns the non editable fields.
    """
    # avoid a circular import
    from django.db.models.fields.related import ManyToManyField
    opts = instance._meta
    data = {}
    for f in opts.fields + opts.many_to_many:
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primry key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[f.name] = []
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                data[f.name] = [obj.pk for obj in f.value_from_object(instance)]
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def render_csv(filename, title_list, data_list):
    """
    Returns .csv response
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    csv_writer = csv.writer(response)

    csv_writer.writerow(title_list)

    for row_item_list in data_list:
        for i in range(0, len(row_item_list)):
            if row_item_list[i]:
                if isinstance(row_item_list[i], datetime.datetime):
                    row_item_list[i] = row_item_list[i].strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(row_item_list[i], datetime.date):
                    row_item_list[i] = row_item_list[i].strftime('%Y-%m-%d')
                elif isinstance(row_item_list[i], datetime.time):
                    row_item_list[i] = row_item_list[i].strftime('%H:%M:%S')
        csv_writer.writerow(row_item_list)

    return response


def run_export_task(app_label, model_name, fields, **kwargs):
    export = Export.objects.create(
        app_label=app_label,
        model_name=model_name
    )
    if settings.USE_SUBPROCESS:
        args = [python_executable(), 'manage.py', 'run_export_task', str(export.pk)] + fields
        start_dt = kwargs.get('start_dt', None)
        end_dt = kwargs.get('end_dt', None)
        include_files = kwargs.get('include_files', None)
        if start_dt and end_dt:
            args += ['--start_dt', start_dt, '--end_dt', end_dt]
        if include_files:
            args += ['--include_files', include_files]
        subprocess.Popen(args)
    else:
        from django.core.management import call_command
        args = [str(export.pk)] + fields
        call_command('run_export_task', *args, **kwargs)

    return export.pk
