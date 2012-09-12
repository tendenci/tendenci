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
