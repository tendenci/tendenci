from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    The command loops through memberships associated to users.
    It then checks if the membership entry information matches
    the profile information.

    It then prints whether information did not match.
    """
    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        from memberships.models import Membership

        users = User.objects.exclude(memberships__isnull=True)

        for user in users:
            mems = Membership.objects.filter(user=user).order_by('create_dt')

            for i, mem in enumerate(mems):
                entry = mems[0].get_entry()

                if not entry:
                    continue  # on to the next one

                if not entry.user:
                    entry.user = user
                    entry.save()

                efn = entry.first_name.lower().strip()
                eln = entry.last_name.lower().strip()
                eem = entry.email.lower().strip()

                ufn = entry.user.first_name.lower().strip()
                uln = entry.user.last_name.lower().strip()
                uem = entry.user.email.lower().strip()

                if not all((efn == ufn, eln == uln, eem == uem)):
                    print 'user(%d) did not match membership(%d) entry(%d)' % \
                    (user.pk, mem.pk, entry.pk)

                    if i == 0:
                        print '; is first membership'

                    print efn or 'blank', ufn or 'blank'
                    print eln or 'blank', uln or 'blank'
                    print eem or 'blank', uem or 'blank'
                    print '-' * 20
