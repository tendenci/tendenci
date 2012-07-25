from datetime import datetime
from celery.task import Task
from celery.registry import tasks
from tendenci.apps.locations.importer.tasks import ImportLocationsTask

tasks.register(ImportLocationsTask)