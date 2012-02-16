from django.core.management.base import BaseCommand

class Command(BaseCommand):
	"""
	example: python manage.py memberships_update_entries
	"""
	def handle(self, *args, **kwargs):
		from memberships.models import Membership, AppEntry, AppFieldEntry, AppField

		try:
			corp_field = AppField.objects.get(field_type='corporate_membership_id')
		except AppField.DoesNotExist:
			return False

		entries = AppEntry.objects.all()

		for entry in entries:
			corp_id = self.get_field_value('corporate_membership_id')

			if corp_id.is_digit():
				pass  # this one is good; on to the next one

			value = entry.membership.corporate_membership_id

			# app_field_entry = AppFieldEntry.objects.create(
			# 	entry=entry,
			# 	field=corp_field,
			# 	value=value,
			# )

			# print app_field_entry, 'created'

		return True