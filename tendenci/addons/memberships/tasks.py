from celery.registry import tasks
from tendenci.addons.memberships.importer.tasks import ImportMembershipsTask

tasks.register(ImportMembershipsTask)
