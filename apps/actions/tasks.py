from celery.decorators import task
from actions.utils import distribute_newsletter_v2

@task()
def task_queue_distribute_newsletter(action, **kwargs):
    logger = task_queue_distribute_newsletter.get_logger(**kwargs)
    logger.info("Processing newsletter %s" % (action.name))
    distribute_newsletter_v2(action, **kwargs)
    return True

    