from celery.registry import tasks

from tendenci.contrib.user_groups.importer.tasks import ImportSubscribersTask


tasks.register(ImportSubscribersTask)
