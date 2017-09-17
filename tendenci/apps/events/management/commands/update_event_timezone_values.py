from dateutil import tz

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Loop through all events and convert their timezone value from
    the default to the value that they are intended to be displayed.

    Only run this once, and after running convert_pg_timestamp_to_tz

    Usage:
        python manage.py update_event_timezone_values
    """
    def handle(self, *args, **options):
        from tendenci.apps.events.models import Event

        for field in Event._meta.fields:
            if field.name == 'update_dt':
                field.auto_now = False

        events = Event.objects.all()
        for ev in events:
            if ev.start_dt and ev.end_dt:
                to_zone = tz.gettz('America/Chicago')
                from_zone = tz.gettz(ev.timezone.__str__())

                current_st = ev.start_dt.replace(tzinfo=from_zone)
                new_st = current_st.astimezone(to_zone)
                ev.start_dt = new_st

                current_et = ev.end_dt.replace(tzinfo=from_zone)
                new_et = current_et.astimezone(to_zone)
                ev.end_dt = new_et

                ev.save()

                for p in ev.registration_configuration.regconfpricing_set.all():
                    currentp_st = p.start_dt.replace(tzinfo=from_zone)
                    newp_st = currentp_st.astimezone(to_zone)
                    p.start_dt = newp_st

                    currentp_et = p.end_dt.replace(tzinfo=from_zone)
                    newp_et = currentp_et.astimezone(to_zone)
                    p.end_dt = newp_et

                    p.save()

        for field in Event._meta.fields:
            if field.name == 'update_dt':
                field.auto_now = True
