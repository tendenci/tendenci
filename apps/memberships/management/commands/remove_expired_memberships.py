from django.core.management.base import BaseCommand

class Command(BaseCommand):
	"""
	Set the status detail of the membership to expired.
	Remove the user from the [privileged] group.
	example: python manage.py remove_expired_memberships
	"""
	def handle(self, *args, **kwargs):
		from datetime import datetime
		from dateutil.relativedelta import relativedelta
		from memberships.models import Membership, MembershipType, MembershipArchive
		from user_groups.models import GroupMembership

		for membership_type in MembershipType.objects.all():
			grace_period = membership_type.expiration_grace_period

			# get expired memberships out of grace period
			memberships = Membership.objects.filter(
				membership_type=membership_type,
				expire_dt__lt=datetime.now()
			)

			for membership in memberships:
		        # update status detail
		        membership.status_detail = 'expired'
		        membership.save()

		        # remove from group
		        GroupMembership.objects.filter(
		            member=membership.user, 
		            group=membership.membership_type.group
		        ).delete()

				if membership.expire_dt < datetime.now()+relativedelta(days=grace_period):
					MembershipArchive.archive(membership)