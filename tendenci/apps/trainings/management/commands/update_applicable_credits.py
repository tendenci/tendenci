from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Populate the applicable credits for each UserCertData.
    
    """
    
    def handle(self, *args, **options):
        from tendenci.apps.trainings.models import (Certification, UserCertData)

        # Populate required_credits for each certification
        for cert in Certification.objects.all():
            cert.cal_required_credits()

        # Populate applicable_credits for each user's cert
        for user_cert_data in UserCertData.objects.all():
            user_cert_data.cal_applicable_credits()
        print('Populated applicable credits')
