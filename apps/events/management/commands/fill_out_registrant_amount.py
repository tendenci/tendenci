from django.core.management.base import BaseCommand, CommandError



class Command(BaseCommand):
    """
    This is a one-time script to fill out the amount field in the event registrant table. 
    
    To run the command: python manage.py fill_out_registrant_amount
    """
    
    def handle(self, *args, **options):
        from events.models import Registration
        registrations = Registration.objects.filter(invoice__subtotal__gt=0)
        
        if registrations:
            print "Start filling out the amount field for Registrant table:"
            for i, reg8n in enumerate(registrations):
                if reg8n.registrant_set.count() == 1:
                    registrant = reg8n.registrant_set.all()[0]
                    if not registrant.amount:
                        registrant.amount = reg8n.invoice.subtotal
                        registrant.save()
                        print '%d. %s %s (id=%d) - amount: %.2f' % (i+1, registrant.first_name, 
                                    registrant.last_name, registrant.id, registrant.amount)
            print "Done"
        else:
            print "No registrations or registrations with payment on the site."