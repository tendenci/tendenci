from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    """
    Handles the porting of data from the Membership and Entries
    model to the MembershipDefault/Profile model.
    """

    def handle(self, *args, **options):
        """
        Loops through AppEntry instances and ports the
        data over to MembershipDefault instances.
        """
        from tendenci.apps.entities.models import Entity
        from tendenci.addons.memberships.models import AppEntry, MembershipDefault
        from tendenci.apps.profiles.models import Profile
        verbosity = options['verbosity']

        for e in AppEntry.objects.all():

            if e.membership:
                # use guid to match records
                m_default = MembershipDefault.objects.first(
                    guid=e.membership.guid,
                )
            else:
                # use create_dt and membership_type
                m_default = MembershipDefault.objects.first(
                    create_dt=e.create_dt,
                    membership_type=e.membership_type,
                )

            if m_default:
                # found; already created
                m_default_created = True
            else:
                # not found; then creating
                m_default_created = False
                m_default = MembershipDefault()

            if e.membership:
                m_default.member_number = e.membership.member_number
                m_default.membership_type = e.membership.membership_type
                m_default.renewal = e.membership.renewal

                m_default.guid = e.membership.guid
                m_default.expire_dt = e.membership.expire_dt

                # m_default.certifications
                # m_default.work_experience
                # m_default.referral_source
                # m_default.referral_source_other
                # m_default.referral_source_member_name
                # m_default.referral_source_member_number
                # m_default.affiliation_member_number
                # m_default.primary_practice
                # m_default.how_long_in_practice
                # m_default.notes
                # m_default.admin_notes
                # m_default.newsletter_type
                # m_default.directory_type
                # m_default.bod_dt
                # m_default.personnel_notified_dt

                # m_default.payment_recieved_dt
                m_default.payment_method = e.membership.payment_method

                # m_default.override
                # m_default.override_price
                # m_default.exported

                # m_default.chapter
                # m_default.areas_of_expertise
                # m_default.organization_entity
                # m_default.corporate_entity

                if e.membership.corporate_membership_id:
                    m_default.corporate_membership_id = e.membership.corporate_membership_id
                else:
                    m_default.corporate_membership_id = None

                # m_default.home_state
                # m_default.year_left_native_country
                # m_default.network_sectors
                # m_default.networking
                # m_default.government_worker
                # m_default.government_agency
                # m_default.license_number
                # m_default.license_state
                # m_default.industry
                # m_default.region
                # m_default.company_size
                # m_default.promotion_code
                # m_default.directory

                if hasattr(e.membership, 'user'):
                    m_default.user = e.membership.user

            if not hasattr(m_default, 'user'):
                m_default.user, user_created = m_default.get_or_create_user(
                    email=e.email, first_name=e.first_name, last_name=e.last_name
                )

            if not hasattr(m_default, 'membership_type'):
                if verbosity:
                    self.echo(
                        m_default, e,
                        created=m_default_created,
                        skipped=True,
                    )

                continue  # on to the next one

            m_default.application_complete_dt = e.create_dt
            m_default.entity = Entity.objects.first()
            m_default.organization_entity = m_default.entity
            m_default.corporate_entity = m_default.entity

            if e.is_approved:
                m_default.application_approved = True
                m_default.application_approved_dt = e.decision_dt
                m_default.application_approved_user = e.judge

                # is a join
                if not e.is_renewal:
                    m_default.join_dt = e.decision_dt
                    m_default.set_join_dt()

            if e.decision_dt:
                m_default.application_approved_denied_dt = e.decision_dt
                m_default.application_approved_denied_user = m_default.user

                m_default.action_taken = True
                m_default.action_taken_dt = e.decision_dt
                m_default.action_taken_user = e.judge

            m_default.set_renew_dt()
            if not m_default.expire_dt:
                m_default.set_expire_dt()

            if not hasattr(m_default.user, 'profile'):
                Profile.objects.create_profile(m_default.user)

            m_default.user.profile.refresh_member_number()

            self.set_owner_creator_fields(m_default, e)
            self.set_allow_fields(m_default, e.membership)
            self.set_status_fields(m_default, e.membership)

            m_default.save()

            self.set_invoice(m_default, e)

            # add user to [membership] group
            m_default.group_refresh()

            # reset create_dt
            self.set_owner_creator_fields(m_default, e)
            m_default.save()

            if verbosity:
                self.echo(m_default, e, created=m_default_created)

    def echo(self, m_default, e, created, skipped=False):
        """
        Prints out message on screen.
        Dependent on Membership and MembershipDefault
        existing
        """

        msg = u'insert'
        if created:
            msg = u'update'

        if skipped:
            msg = 'skipped'

        if e.membership:
            print 'Membership %s ==> MembershipDefault %s (%s)' % (
                e.membership.pk, m_default.pk, msg)
        else:
            print 'Entry %s ==> MembershipDefault %s (%s)' % (
                e.pk, m_default.pk, msg)

    def set_invoice(self, m_default, e):
        """
        If AppEntry has invoice then associate
        Invoice with MembershipDefault.
        """
        from tendenci.apps.invoices.models import Invoice

        entry_ct = ContentType.objects.get_for_model(e)
        m_default_ct = ContentType.objects.get_for_model(m_default)

        # get invoice [associated w/ entry]
        invoice = Invoice.objects.first(
            object_type=entry_ct,
            object_id=e.pk
        )

        # associate invoice w/ m_default
        if invoice:
            invoice.object_type = m_default_ct
            invoice.object_id = m_default.pk
            invoice.save()

    def set_owner_creator_fields(self, m_default, entry):
        """
        Set owner and creator fields.
        """

        if entry.membership:
            m_default.creator = entry.membership.creator
            m_default.creator_username = entry.membership.creator.username
            m_default.create_dt = entry.membership.create_dt
            m_default.owner = entry.membership.owner
            m_default.owner_username = entry.membership.owner.username
            m_default.update_dt = entry.membership.update_dt
        else:
            m_default.creator = entry.creator
            m_default.creator_username = entry.creator_username
            m_default.create_dt = entry.create_dt
            m_default.owner = entry.owner
            m_default.owner_username = entry.owner_username
            m_default.update_dt = entry.update_dt

    def set_allow_fields(self, m_default, membership):
        """
        Set allow fields.  Use safe [private] defaults.
        """

        if membership:
            m_default.allow_anonymous_view = membership.allow_anonymous_view
            m_default.allow_user_view = membership.allow_user_view
            m_default.allow_member_view = membership.allow_member_view
            m_default.allow_anonymous_edit = False
            m_default.allow_user_edit = membership.allow_user_edit
            m_default.allow_member_edit = membership.allow_member_edit
        else:
            m_default.allow_anonymous_view = False
            m_default.allow_user_view = False
            m_default.allow_member_view = False
            m_default.allow_anonymous_edit = False
            m_default.allow_user_edit = False
            m_default.allow_member_edit = False

    def set_status_fields(self, m_default, membership):
        """
        Set status and status_detail
        """

        if membership:
            m_default.status = membership.status
            m_default.status_detail = membership.status_detail
        else:
            m_default.status = False
            m_default.status_detail = 'inactive'
