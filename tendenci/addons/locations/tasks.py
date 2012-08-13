from datetime import datetime
from celery.task import Task
from celery.registry import tasks
from tendenci.addons.locations.importer.tasks import ImportLocationsTask

tasks.register(ImportLocationsTask)