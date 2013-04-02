from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This command checks membership entries and confirms
    whether they are blank by setting status_detail to 'empty.'
    """
    def handle(self, *args, **options):
        from django.contrib.contenttypes.models import ContentType
        from tendenci.apps.invoices.models import Invoice
        from tendenci.addons.memberships.models import MembershipDefault

        content_type = ContentType.objects.get_for_model(MembershipDefault)
        invoices = Invoice.objects.filter(
            object_type=content_type).order_by('create_dt')

        total_count = invoices.count()

        i = 0
        lst = []
        lst.append([])

        b = None
        for a in invoices:

            if b:

                delta = (a.create_dt - b.create_dt)
                if delta.total_seconds() < 10:
                    lst[i].append(a)
                    lst[i].append(b)
                else:
                    if lst[i]:
                        i = i+1
                        lst.append([])  # list of lists

            b = a  # set for next round

        # remove dupes; side-effect: unsorts
        lst = [list(set(l)) for l in lst]

        # resort; count imported
        imported_count = 0
        for l in lst:  # resort
            imported_count = imported_count + len(l)  # count imported_count
            l.sort(key=lambda x: x.create_dt)

        for l in lst:
            for m in l:
                print m
                m.delete()

        self.print_results(lst, imported_count, total_count)

    def print_results(self, lst, imported_count, total_count):
        """
        Prints summary of results
        """
        for i, l in enumerate(lst):
            if l:
                print i+1, len(l), sum(self.delta(l))/len(l), min(self.delta(l)), max(self.delta(l))

        print '-'*50
        print 'imported:', imported_count
        print 'total:', total_count
        print 'legit:', total_count-imported_count

    def delta(self, lst):
        """
        Accepts a list of invoices.
        Returns a list of deltas (total_seconds).
        """
        m = None
        new_list = []
        for l in lst:

            if m:
                new_list.append((l.create_dt - m.create_dt).total_seconds())
            m = l

        return new_list






