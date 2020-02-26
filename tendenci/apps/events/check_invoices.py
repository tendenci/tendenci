
from django.contrib.contenttypes.models import ContentType
from tendenci.apps.events.models import Registration
from tendenci.apps.invoices.models import Invoice

regs = Registration.objects.all()

for reg in regs:
    print(reg.invoice)
    if not reg.invoice:
        #no invoice associated, check from invoice model
        object_type = ContentType.objects.get(app_label=reg._meta.app_label,
            model=reg._meta.model_name)
        try:
            inv = Invoice.objects.get(object_type = object_type, object_id = reg.pk)
        except Invoice.DoesNotExist:
            inv = None

        if inv:
            print(inv, "invoice found for", reg.pk)
