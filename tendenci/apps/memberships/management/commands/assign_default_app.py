
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Assign (and correct) the app field for the membership_defaults.

    Usage: python manage.py assign_default_app --verbosity 2
    """

    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']

        from tendenci.apps.memberships.models import (
                                            MembershipApp,
                                            MembershipType,
                                            MembershipDefault)
        from tendenci.apps.corporate_memberships.models import CorpMembershipApp

        memberships = MembershipDefault.objects.all()
        errors = ''
        corp_app = None
        if memberships.filter(corporate_membership_id__gt=0).exists():
            corp_app = CorpMembershipApp.objects.current_app()
            if not corp_app:
                errors += 'Missing a corporate membership application.\n'
            else:
                if not hasattr(corp_app, 'memb_app') \
                        or not corp_app.memb_app:
                    errors += 'No membership application is associated ' + \
                            'with the corporate membership application ' + \
                            '"%s".\n' % corp_app.name
        if memberships.exclude(corporate_membership_id__gt=0).exists():
            [app] = MembershipApp.objects.filter(
                           status=True,
                           status_detail__in=['active', 'published']
                           ).exclude(use_for_corp=True
                           ).order_by('id')[:1] or [None]
            if not app:
                errors += 'Missing a membership application ' + \
                          '(for non-corporate-individuals).\n'
        if errors:
            print('\nWARNING:')
            print(errors)
            print('Please correct the issue(s) then ' +
                    'run this command "assign_default_app" again.\n')
            return

        mts = MembershipType.objects.all()
        # map types to a list of apps
        type_to_apps_map = {}
        for mt in mts:
            membership_apps = MembershipApp.objects.filter(
                                    membership_types__in=[mt]
                                    ).order_by('id')
            if membership_apps:
                type_to_apps_map[mt.id] = membership_apps
            else:
                type_to_apps_map[mt.id] = [app]

        count = 0
        for membership in memberships:
            if membership.corporate_membership_id:
                # corp individuals
                if not membership.app_id or \
                        membership.app_id != corp_app.memb_app_id:
                    membership.app_id = corp_app.memb_app_id
                    membership.save()
                    count += 1
                    if verbosity > 1:
                        print('Updated "%s" (ID: %d)' % (membership,
                                                         membership.id))
            else:
                mt_id = membership.membership_type.id
                if membership.app not in type_to_apps_map[mt_id]:
                    membership.app = type_to_apps_map[mt_id][0]
                    membership.save()
                    count += 1
                    if verbosity > 1:
                        print('Updated "%s" (ID: %d)' % (membership,
                                                         membership.id))

        print('Total membership updated %d' % count)
        print('Done')
