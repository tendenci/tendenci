from django.core.management.base import BaseCommand

class Command(BaseCommand):
	"""
	example: python manage.py remove_expired_memberships
	"""
	def handle(self, *args, **kwargs):
		from datetime import datetime
		from memberships.models import Membership
		from user_groups.models import GroupMembership

		## get list of expired memberships
		memberships = Membership.objects.filter(expiration_dt__lt = datetime.now())

		# # Change status_detail to expired
		# # My only problem with this currently is having
		# # to check 2 locations to deciper whether someone is expired
		# members = []
		# for member in memberships:
		# 	member.status_detail = 'expired'
		# 	member.save()
		# 	members.append(member)

		members = [m.user for m in memberships]

		group_memberships = GroupMembership.objects.filter(member__in = members)
		group_memberships.delete()  # remove records