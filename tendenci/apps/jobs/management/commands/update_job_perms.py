from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    example: python manage.py update_job_perms
    """
    def handle(self, *event_ids, **options):
        from django.contrib.auth.models import Permission
        from tendenci.apps.jobs.models import JobPricing

        # update permission
        Permission.objects.filter(codename='view_job_pricing').update(codename='view_jobpricing')

        # reindex job instances via save()
        pricing_set = JobPricing.objects.all()
        for pricing in pricing_set:
            pricing.save()