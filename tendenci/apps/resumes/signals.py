from django.utils.translation import ugettext_noop as _
from tendenci.apps.notifications import models as notification


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    
    notification.create_notice_type("resume_added",
                                    _("Resume Added"),
                                    _("A resume has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("resume_deleted",
                                    _("Resume Deleted"),
                                    _("A resume has been deleted"),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.resumes.models import Resume
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Resume, weak=False)
