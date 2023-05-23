from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Clean up old (>3 days) transcript PDF zip files

    Usage:
        python manage.py clean_old_transcript_pdfs

    """
    def handle(self, *args, **options):
        from datetime import datetime, timedelta
        from tendenci.apps.trainings.models import CorpTranscriptsZipFile
        print("Cleanning up old transcript PDFs")
        for tz in CorpTranscriptsZipFile.objects.all():
            if tz.start_dt + timedelta(days=3) < datetime.now():
                print(f"Deleting transcript zip file (pk={tz.id})")
                tz.delete()
        print("Done")
