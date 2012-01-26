from django.core.management.base import BaseCommand

class Command(BaseCommand):
	"""
	example: python manage.py remove_expired_memberships
	"""
	def handle(self, *args, **kwargs):
		from datetime import datetime
		from memberships.models import Membership
		from user_groups.models import GroupMembership

		# get memberships that have expired
		expired_memberships = Membership.objects.filter(
			expire_dt__lt = datetime.now())

		# update status detail
		for membership in expired_memberships:

			# update status detail
			membership.status_detail = 'expired'
			membership.save()

			# remove groupmembership
			GroupMembership.objects.filter(
				member=membership.user, 
				group=membership.membership_type.group
			).delete()