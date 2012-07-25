from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'A run once only script. Converts the old name \
            field in registrants to first_name, last_name'

    def convert_name(self, name):
        name_list = [n for n in name.split() if n]
        suffixes = ['jr', 'jr.', 'sr', 'sr.', 'md',
                    'm.d' 'm.d.', 'phd', 'ph.d', 'i',
                    'ii', 'iii']
        prefix = first = middle = last = suffix = ''
        first_name, last_name = '', ''

        if len(name_list) == 5:
            prefix, first, middle, last, suffix = name_list
            first_name = '%s %s %s' % (
                prefix,
                first,
                middle,
            )
            last_name = '%s %s' % (
                last,
                suffix,
            )
        elif len(name_list) == 4:
            first, middle, last, suffix = name_list
            first_name = '%s %s' % (
                first,
                middle,
            )
            last_name = '%s %s' % (
                last,
                suffix,
            )
        elif len(name_list) == 3:
            first, middle, last = name_list
            if last.lower() in suffixes:
                first_name = first
                last_name = '%s %s' % (
                    middle,
                    last,
                )
            else:
                first_name = '%s %s' % (
                    first,
                    middle,
                )
                last_name = last
        elif len(name_list) == 2:
            first, last = name_list
            first_name = first
            last_name = last
        elif len(name_list) == 1:
            first = name_list[0]
            first_name = first
        else:
            first = name
            first_name = first

        # clean the names up
        first_name = first_name.strip()
        first_name = first_name.replace(',','')
        last_name = last_name.strip()
        last_name = last_name.replace(',','')

        return (first_name, last_name,)
        
    def handle(self, *args, **options):
        verbosity = options['verbosity']
        count = 0
        from tendenci.apps.events.models import Registrant
        registrants = Registrant.objects.all()
        if registrants:
            for registrant in registrants:
                if registrant.name:
                    fn, ln = self.convert_name(registrant.name)
                    registrant.first_name = fn
                    registrant.last_name = ln
                    if verbosity == 2:
                        try:
                            print '%s (%s -- %s)' % (registrant.name, registrant.last_name, registrant.first_name,)
                        except:
                            pass
                    registrant.save()
                    count += 1
        print 'Separated %d registrant names to first_name and last_name' % count
