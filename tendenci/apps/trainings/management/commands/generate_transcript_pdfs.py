
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    Transcript PDFs generator for corp.

    Usage:
        python manage.py generate_transcript_pdfs <id>

        example:
        python manage.py generate_transcript_pdfs 1

    """
    def add_arguments(self, parser):
        parser.add_argument('id', type=int)

    def handle(self, *args, **options):
        import zipfile
        import datetime
        from tempfile import NamedTemporaryFile
        from django.contrib.auth.models import User
        from tendenci.apps.emails.models import Email
        from tendenci.apps.trainings.models import CorpTranscriptsZipFile, Certification, CertCat, Course
        from tendenci.apps.corporate_memberships.models import CorpProfile
        from tendenci.apps.trainings.utils import generate_transcript_pdf

        # Validating data that are passed in

        tz_id = options.get('id', None)
        if not tz_id:
            msg = 'Please pass id of CorpTranscriptsZipFile'
            raise CommandError(msg)
        
        try:
            tz = CorpTranscriptsZipFile.objects.get(pk=tz_id)
        except CorpTranscriptsZipFile.DoesNotExist:
            msg = f'CorpTranscriptsZipFile table does not have id={tz_id}'
            raise CommandError(msg)

        corp_profile_id = tz.corp_profile_id
        [corp_profile] = CorpProfile.objects.filter(id=corp_profile_id)[:1] or [None]
        if not corp_profile:
            raise CommandError('Corp Profile does not exist.')

        print("Generating transcript PDFs for corp ...")

        # Preparing data needed to generate user PDFs

        # get a list of cert objects
        cert_ids = tz.params_dict['certs'].split(',')
        certs = Certification.objects.filter(id__in=cert_ids)
        for cert in certs:
            cert.certcats = []
            cats = cert.categories.all()
            for cat in cats:
                [certcat] = CertCat.objects.filter(certification=cert, category=cat)[:1] or [None]
                if certcat:
                    cert.certcats.append(certcat)
        users = User.objects.filter(id__in=tz.params_dict['users'].split(','))
        params = {}
        params['certs'] = certs
        params['corp_profile'] = corp_profile
        if tz.params_dict['online_courses']:
            params['online_courses'] = Course.objects.filter(id__in=tz.params_dict['online_courses'].split(','))
        else:
            params['online_courses'] = None
        if tz.params_dict['onsite_courses']:
            params['onsite_courses'] = Course.objects.filter(id__in=tz.params_dict['onsite_courses'].split(','))
        else:
            params['onsite_courses'] = None
        params['include_outside_schools'] = tz.params_dict['include_outside_schools']
        params['include_teaching_activities'] = tz.params_dict['include_teaching_activities']

        dt = datetime.datetime.now().strftime('%Y_%m%d_%H%M%S_%f')
        zip_name = f'transcripts_{dt}.zip'
        
        # Generating zip file for each user in the corp

        temp_zip = NamedTemporaryFile(mode='wb', delete=False)
        with zipfile.ZipFile(temp_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for user in users:
                params['customer'] = user
                temp_f = NamedTemporaryFile(mode='wb', delete=False)
                generate_transcript_pdf(temp_f, **params)
                temp_f.close()
                file_name = f"transcript_{user.username}.pdf"
                archive.write(temp_f.name, arcname=file_name, compress_type=zipfile.ZIP_DEFLATED)

        # Saving file and updating status

        with open(temp_zip.name, 'rb') as temp_zip_f:
            tz.zip_file.save(zip_name, temp_zip_f)

        tz.status = "completed"
        tz.finish_dt = datetime.datetime.now()
        tz.save()

        # Sending email to the creator

        context = { 'obj': tz, 'creator': tz.creator }
        email_subject = f"Your transcript PDFs (id:{tz.id}) is ready for download"
        email_body = render_to_string(template_name="trainings/transcript_pdfs_ready_email_body.html", context=context)
        email = Email(recipient=tz.creator.email, subject=email_subject, body=email_body)
        email.send()

        print("Done!")
