from celery.registry import tasks
from user_groups.importer.tasks import ImportSubscribersTask

tasks.register(ImportSubscribersTask)
