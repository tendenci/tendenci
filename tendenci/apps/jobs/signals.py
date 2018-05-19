from django.utils.translation import ugettext_noop as _
from tendenci.apps.notifications import models as notification


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("job_added",
                                    _("Job Added"),
                                    _("A job has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("job_deleted",
                                    _("Job Deleted"),
                                    _("A job has been deleted"),
                                    verbosity=verbosity)
    notification.create_notice_type("job_approved_user_notice",
                                    _("Job Approved User Notice"),
                                    _("A job has been approved - user notice."),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.jobs.models import Job
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Job, weak=False)
