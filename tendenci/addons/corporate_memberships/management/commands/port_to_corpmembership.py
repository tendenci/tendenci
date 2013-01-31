from decimal import Decimal
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str
from django.db.models.fields import AutoField
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    """
    Port the corporate memberships from old system CorporateMembership
    to the new system CorpMembership.

    Usage:
            ./manage.py port_to_corpmembership --verbosity 2
    """
    def handle(self, **options):
        from tendenci.addons.corporate_memberships.models import (
                                                  CorpProfile,
                                                  CorpMembership,
                                                  CorporateMembership)
        from tendenci.addons.memberships.models import MembershipDefault
        verbosity = int(options['verbosity'])

        corp_profile_field_names = [smart_str(field.name) for field \
                               in CorpProfile._meta.fields \
                             if not field.__class__ == AutoField]
        corp_membership_field_names = [smart_str(field.name) for field \
                               in CorpMembership._meta.fields \
                             if not field.__class__ == AutoField]
        corp_profile_fields = dict([(field.name, field) \
                            for field in CorpProfile._meta.fields \
                            if field.get_internal_type() != 'AutoField' and \
                            field.name not in ['guid']])
        corp_membership_fields = dict([(field.name, field) \
                            for field in CorpMembership._meta.fields \
                            if field.get_internal_type() != 'AutoField' and \
                            field.name not in ['user', 'guid',
                                               'corp_profile']])

        def get_default_value(field):
            # if allows null or has default, return None
            if field.null or field.has_default():
                return None

            field_type = field.get_internal_type()

            if field_type == 'BooleanField':
                return False

            if field_type == 'DateField':
                return date

            if field_type == 'DateTimeField':
                return datetime.now()

            if field_type == 'DecimalField':
                return Decimal(0)

            if field_type == 'IntegerField':
                return 0

            if field_type == 'FloatField':
                return 0

            if field_type == 'ForeignKey':
                if not field.name in ['creator', 'owner']:
                    [value] = field.related.parent_model.objects.all(
                                                )[:1] or [None]
                    return value
                return None

            return ''

        corporates = CorporateMembership.objects.all()

        for corporate in corporates:
            # check if corp_profile already exists
            [corp_profile] = CorpProfile.objects.filter(name=corporate.name)[:1] or [None]
            if not corp_profile:
                corp_profile = CorpProfile()
                for field_name in corp_profile_field_names:
                    if hasattr(corporate, field_name):
                        value = getattr(corporate, field_name)
                    else:
                        value = None
                    if value is None and field_name in corp_profile_fields:
                        value = get_default_value(corp_profile_fields[field_name])
                    if not value is None:
                        setattr(corp_profile, field_name,
                                value)
                corp_profile.save()

                if verbosity >= 2:
                    print 'Insert corp_profile: ', corp_profile
                corp_membership = None
            else:
                # check if corp_membership exists
                corp_membership = corp_profile.corp_membership
            if not corp_membership:
                corp_membership = CorpMembership()
                for field_name in corp_membership_field_names:
                    if hasattr(corporate, field_name):
                        value = getattr(corporate, field_name)
                    else:
                        value = None
                    if value is None and field_name in corp_membership_fields:
                        value = get_default_value(corp_membership_fields[field_name])
                    if not value is None:
                        setattr(corp_membership, field_name,
                                value)

                corp_membership.corp_profile = corp_profile
                corp_membership.save()

                # update invoice object_type and object_id
                if corp_membership.invoice:
                    corp_membership.invoice.object_type = ContentType.objects.get(
                                  app_label=corp_membership._meta.app_label,
                                  model=corp_membership._meta.module_name)
                    corp_membership.invoice.object_id = corp_membership.id
                    corp_membership.invoice.save()

                if verbosity >= 2:
                    print 'Insert corp_membership (id=%d) for: ' % corp_membership.id, corp_profile

            # update individual membership entries
            memberships = MembershipDefault.objects.filter(
                corporate_membership_id=corporate.pk,
                corp_profile_id=0
            )

            for membership in memberships:
                membership.corp_profile_id = corp_profile.pk
                membership.corporate_membership_id = corp_membership.pk
                membership.save()
                if verbosity >= 2:
                    print 'Updated membership (id=%d):' % membership.id, membership
