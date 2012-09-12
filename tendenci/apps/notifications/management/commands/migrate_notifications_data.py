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
            next_id = int(models.NoticeType.objects.order_by('-id')[0].pk) + 1
            models.NoticeType.objects.raw("SELECT setval('notifications_noticetype_id_seq', %d)" % next_id)
        except:
            pass

        # NoticeSetting
        try:
            for i in models.NoticeSetting.objects.raw('SELECT * FROM notification_noticesetting'):
                i.save()
            next_id = int(models.NoticeSetting.objects.order_by('-id')[0].pk) + 1
            models.NoticeSetting.objects.raw("SELECT setval('notifications_noticesetting_id_seq', %d)" % next_id)
        except:
            pass

        # Notice
        try:
            for i in models.Notice.objects.raw('SELECT * FROM notification_notice'):
                i.save()
            next_id = int(models.Notice.objects.order_by('-id')[0].pk) + 1
            models.Notice.objects.raw("SELECT setval('notifications_notice_id_seq', %d)" % next_id)
        except:
            pass

        # NoticeQueueBatch
        try:
            for i in models.NoticeQueueBatch.objects.raw('SELECT * FROM notification_noticequeuebatch'):
                i.save()
            next_id = int(models.NoticeQueueBatch.objects.order_by('-id')[0].pk) + 1
            models.NoticeQueueBatch.objects.raw("SELECT setval('notifications_noticequeuebatch_id_seq', %d)" % next_id)
        except:
            pass

        # NoticeEmail
        try:
            for i in models.NoticeEmail.objects.raw('SELECT * FROM notification_noticeemail'):
                i.save()
            next_id = int(models.NoticeEmail.objects.order_by('-id')[0].pk) + 1
            models.NoticeEmail.objects.raw("SELECT setval('notifications_noticeemail_id_seq', %d)" % next_id)
        except:
            pass

        # ObservedItem
        try:
            for i in models.ObservedItem.objects.raw('SELECT * FROM notification_observeditem'):
                i.save()
            next_id = int(models.ObservedItem.objects.order_by('-id')[0].pk) + 1
            models.ObservedItem.objects.raw("SELECT setval('notifications_observeditem_id_seq', %d)" % next_id)
        except:
            pass
