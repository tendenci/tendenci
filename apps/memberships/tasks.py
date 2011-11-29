from datetime import datetime
from celery.task import Task
from celery.registry import tasks

from memberships.models import AppEntry, AppField, AppFieldEntry
from memberships.importer.tasks import ImportMembershipsTask

tasks.register(ImportMembershipsTask)
