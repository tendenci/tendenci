from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    This is a one-time script to fill out the amount field in the event registrant table. 
    
    To run the command: python manage.py fill_out_registrant_amount --verbosity 2
    """
    
    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']

        from tendenci.addons.events.models import Registration
        registrations = Registration.objects.filter(invoice__subtotal__gt=0)
        
        if registrations:
            print "Start filling out the amount field for Registrant table:"
            count = 0
            for i, reg8n in enumerate(registrations):
                if reg8n.registrant_set.count() == 1:
                    registrant = reg8n.registrant_set.all()[0]
                    if not registrant.amount:
                        registrant.amount = reg8n.invoice.subtotal
                        registrant.save()
                        count += 1
                        if verbosity >= 2:
                            try:
                                print 'id=', registrant.id, registrant.first_name, registrant.last_name, registrant.amount
                            except:
                                pass
            print 'Total updated: %d' % (count)
            print "Done"
        else:
            print "No registrations or registrations with payment on the site."