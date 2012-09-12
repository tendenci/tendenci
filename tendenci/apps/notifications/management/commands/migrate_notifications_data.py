from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Command to move data from previous table names (singular notification)

    example: python manage.py move_from_old_table
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.notifications import models

        # NoticeType
        try:
            for i in models.NoticeType.objects.raw('SELECT * FROM notification_noticetype'):
                i.save()
        except:
            pass

        # NoticeSetting
        try:
            for i in models.NoticeSetting.objects.raw('SELECT * FROM notification_noticesetting'):
                i.save()
        except:
            pass

        # Notice
        try:
            for i in models.Notice.objects.raw('SELECT * FROM notification_notice'):
                i.save()
        except:
            pass

        # NoticeQueueBatch
        try:
            for i in models.NoticeQueueBatch.objects.raw('SELECT * FROM notification_noticequeuebatch'):
                i.save()
        except:
            pass

        # NoticeEmail
        try:
            for i in models.NoticeEmail.objects.raw('SELECT * FROM notification_noticeemail'):
                i.save()
        except:
            pass

        # ObservedItem
        try:
            for i in models.ObservedItem.objects.raw('SELECT * FROM notification_observeditem'):
                i.save()
        except:
            pass

        # Update the auto increments on the ID fields
        models.NoticeType.objects.raw('SELECT setval(pg_get_serial_sequence(\'"notifications_noticetype"\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_noticetype"')
        models.NoticeSetting.objects.raw('SELECT setval(pg_get_serial_sequence(\'"notifications_noticesetting"\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_noticesetting"')
        models.Notice.objects.raw('SELECT setval(pg_get_serial_sequence(\'"notifications_notice"\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_notice"')
        models.NoticeQueueBatch.objects.raw('SELECT setval(pg_get_serial_sequence(\'"notifications_noticequeuebatch"\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_noticequeuebatch"')
        models.NoticeEmail.objects.raw('SELECT setval(pg_get_serial_sequence(\'"notifications_noticeemail"\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_noticeemail"')
        models.ObservedItem.objects.raw('SELECT setval(pg_get_serial_sequence(\'"notifications_observeditem"\',\'id\'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "notifications_observeditem"')
