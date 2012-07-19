from celery.registry import tasks
from memberships.importer.tasks import ImportMembershipsTask

tasks.register(ImportMembershipsTask)
