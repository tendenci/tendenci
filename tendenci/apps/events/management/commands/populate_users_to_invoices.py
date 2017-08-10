from __future__ import print_function
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Populate invoices with creator IDs from registrations.
    """
    def handle(self, *args, **options):
        from tendenci.apps.events.models import Registration
        from tendenci.apps.invoices.models import Invoice

        registrations = Registration.objects.filter(creator__isnull=False)
        
        for registration in registrations:
            related_invoice = Invoice.objects.filter(id=registration.invoice_id)
            for invoice in related_invoice:
                invoice.creator_id = registration.creator_id
                invoice.save()
                print('Invoice %s updated for Registraion %s' % (invoice.id, registration.id))