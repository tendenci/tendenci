from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Populate the usercertdata.
    
    Usage:
          python manage.py populate_usercertdata
    """
    
    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        from tendenci.apps.trainings.models import (Certification,
                                                    Transcript, UserCertData)

        for user in User.objects.filter(id__in=Transcript.objects.values_list('user_id', flat=True)):
            print('Processing user', user)
            for cert in Certification.objects.all():
                if not UserCertData.objects.filter(user=user, certification=cert).exists():
                    UserCertData.objects.create(user=user, certification=cert)
        print('Done')
