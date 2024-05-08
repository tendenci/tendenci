from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Calculate and grant diamond certifications.
    
    Set a daily cron job:
    1 20 * * * /src/venv/bin/python /var/www/tendenci_site/manage.py check_and_grant_diamonds
    """
    
    def handle(self, *args, **options):
        from tendenci.apps.trainings.models import (Certification,
                                                    Transcript, UserCertData)

        for cert in Certification.objects.filter(enable_diamond=True):
            print('Processing ', cert)
            users = User.objects.all()
            for user in users:
                if not Transcript.objects.filter(certification_track=cert, user=user).exists():
                    continue

                cert_data, created = UserCertData.objects.get_or_create(
                                        user=user,
                                        certification=cert)
                if not cert_data.certification_dt:
                    # check if requirements are all met, so that we can mark it as completed by setting certification_dt
                    if cert.is_requirements_met(user):
                        cert_data.certification_dt = date.today()
                        cert_data.save()
                    continue
                continue # skip the diamond for now
                
                d_number = cert_data.get_next_d_number()
                if cert.is_requirements_met(user, diamond_number=d_number):
                    if d_number == 1:
                        # has it been one year since certification date
                        if  cert_data.certification_dt + relativedelta(months=cert.period) <= date.today():
                            setattr(cert_data, f'diamond_{d_number}_dt', date.today())
                            cert_data.save()
                    else:
                        last_diamond_date = getattr(cert_data, f'diamond_{d_number - 1}_dt')
                        if last_diamond_date + relativedelta(months=cert.diamond_period) <= date.today():
                            setattr(cert_data, f'diamond_{d_number}_dt', date.today())
                            cert_data.save()
