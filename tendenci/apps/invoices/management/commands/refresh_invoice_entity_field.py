from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Refresh the new entity field for invoice model based on the object_type
    and object_id.

    Usage:
        .manage.py refresh_invoice_entity_field
    """
    def handle(self, *args, **options):
        from tendenci.apps.invoices.models import Invoice

        invoices = Invoice.objects.all()
        for invoice in invoices:
            entity = invoice.entity
            new_entity = invoice.get_entity()
            if entity != new_entity:
                invoice.entity = new_entity
                invoice.save()
        print 'done'