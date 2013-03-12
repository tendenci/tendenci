import subprocess

from django.conf import settings

from tendenci.core.exports.models import Export


def run_invoice_export_task(app_label, model_name, start_dt, end_dt):
    export = Export.objects.create(
        app_label=app_label,
        model_name=model_name,
    )

    if settings.USE_SUBPROCESS:
        subprocess.Popen(['python', 'manage.py', 'run_invoice_export_task', unicode(export.pk), start_dt, end_dt])
    else:
        from django.core.management import call_command
        args = [unicode(export.pk), start_dt, end_dt]
        call_command('run_invoice_export_task', *args)

    return export.pk
