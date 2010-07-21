from celery.task import Task
from celery.registry import tasks

class ProcessNewsletter(Task):
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info('Processed Newsletter')
        return True

tasks.register(ProcessNewsletter)