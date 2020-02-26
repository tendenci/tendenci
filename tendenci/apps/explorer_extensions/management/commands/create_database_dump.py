
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.core.files.base import ContentFile


class Command(BaseCommand):
    """
    Database Dump

    Usage:
        python manage.py create_database_dump <user_id> <export_format>

        example:
        python manage.py create_database_dump 1 json

    """
    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)
        parser.add_argument('export_format', type=str)
        parser.add_argument('obj_id', type=int, nargs='?')

    def handle(self, *args, **options):
        import datetime
        import uuid
        from django.core.management import call_command
        from django.contrib.auth.models import User
        from tendenci.apps.emails.models import Email
        from tendenci.apps.explorer_extensions.models import DatabaseDumpFile, VALID_FORMAT_CHOICES

        dump_obj = None
        d_id = options.get('obj_id', None)
        if d_id:
            dump_obj = DatabaseDumpFile.objects.filter(pk=d_id)
            if dump_obj.exists():
                dump_obj = dump_obj[0]
            else:
                dump_obj = None

        if not dump_obj:
            dump_obj = DatabaseDumpFile()

        user_id = int(options['user_id'])

        if user_id == 0:
            msg = 'User ID is required. Usage: ./manage.py create_database_dump <user_id>'
            raise CommandError(msg)

        author = User.objects.filter(pk=user_id)
        if author.exists():
            author = author[0]
        else:
            author = None

        if not author:
            raise CommandError('Nonexistent user.')

        dump_obj.author = author

        fmt = options['export_format']

        if fmt not in VALID_FORMAT_CHOICES:
            raise CommandError('Format %s is not supported. Please use one of the following: %s' % (fmt, VALID_FORMAT_CHOICES))

        dump_obj.export_format = fmt
        dump_obj.save()

        print("Creating database dump...")

        content = ''
        dump_obj.dbfile.save(str(uuid.uuid4()), ContentFile(content))
        call_command('dumpdata', format=fmt, output=dump_obj.dbfile.path, exclude=['captcha.captchastore', 'files.multiplefile', 'events.standardregform', 'help_files', 'explorer_extensions'])

        dump_obj.status = "completed"
        dump_obj.end_dt = datetime.datetime.now() + datetime.timedelta(days=3)
        dump_obj.save()

        # File is created.
        # Send email to author
        context = { 'obj':dump_obj, 'author':dump_obj.author }
        email_subject = "Your database export (id:%d) is ready for download" % dump_obj.id
        email_body = render_to_string(template_name="explorer/dbdump_ready_email_body.html", context=context)
        email = Email(recipient=dump_obj.author.email, subject=email_subject, body=email_body)
        email.send()

        print("Done!")
