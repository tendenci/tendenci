from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    Database Dump

    Usage:
        python manage.py create_database_dump <user_id> <export_format>

        example:
        python manage.py create_database_dump 1 json

    """
    def handle(self, *args, **options):
        import datetime
        import uuid
        from StringIO import StringIO
        from django.core.management import call_command
        from django.core.files import File
        from django.contrib.auth.models import User
        from tendenci.apps.emails.models import Email
        from tendenci.apps.explorer_extensions.models import DatabaseDumpFile, VALID_FORMAT_CHOICES
        from tendenci.apps.site_settings.utils import get_setting

        dump_obj = None
        if len(args) > 2:
            d_id = int(args[2])
            dump_obj = DatabaseDumpFile.objects.filter(pk=d_id)
            if dump_obj.exists():
                dump_obj = dump_obj[0]
            else:
                dump_obj = None

        if not dump_obj:
            dump_obj = DatabaseDumpFile()

        user_id = int(args[0])

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

        fmt = None
        if len(args) > 1:
            fmt = args[1]

        if not fmt:
            raise CommandError('Format is required. Usage: ./manage.py create_database_dump <user_id>')
        if fmt not in VALID_FORMAT_CHOICES:
            raise CommandError('Format %s is not supported. Please use one of the following: %s' % (fmt, VALID_FORMAT_CHOICES))

        dump_obj.export_format = fmt
        dump_obj.save()

        print "Creating database dump..."

        content = StringIO()
        call_command('dumpdata', format=fmt, stdout=content, exclude=['captcha.captchastore', 'files.multiplefile', 'events.standardregform', 'help_files', 'explorer_extensions'])

        dump_obj.dbfile.save(str(uuid.uuid1()), File(content))

        dump_obj.status = "completed"
        dump_obj.end_dt = datetime.datetime.now() + datetime.timedelta(days=3)
        dump_obj.save()

        # File is created.
        # Send email to author
        context = { 'obj':dump_obj, 'author':dump_obj.author }
        email_subject = "Your database export (id:%d) is ready for download" % dump_obj.id
        email_body = render_to_string("explorer/dbdump_ready_email_body.html", context)
        email = Email(recipient=dump_obj.author.email, subject=email_subject, body=email_body)
        email.send()

        print "Done!"
