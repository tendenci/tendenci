from celery.registry import tasks
from tendenci.apps.memberships.importer.tasks import ImportMembershipsTask

tasks.register(ImportMembershipsTask)
