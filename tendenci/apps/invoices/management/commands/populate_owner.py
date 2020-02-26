
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Populate the invoice owner.

    Usage:
        python manage.py populate_owner
    """
    def handle(self, *args, **options):
        from tendenci.apps.invoices.models import Invoice

        invoices = Invoice.objects.all()
        for invoice in invoices:
            if not invoice.owner and invoice.object_type:
                obj = invoice.get_object()
                if obj:
                    owner = None
                    if invoice.object_type.model == 'membershipdefault':
                        owner = obj.user
                    elif invoice.object_type.model == 'membershipset':
                        owner = obj.memberships[0].user
                    else:
                        if obj.owner:
                            owner = obj.owner

                    if owner:
                        invoice.set_owner(owner)
                        invoice.save()
        print('done')
