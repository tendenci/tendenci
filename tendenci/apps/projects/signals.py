from django.db.models.signals import post_save
from django.utils.translation import gettext_noop as _

from tendenci.apps.notifications import models as notification
from tendenci.apps.projects.models import Project
from tendenci.apps.contributions.signals import save_contribution


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("project_added",
                                    _("Project Added"),
                                    _("A project has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("project_approved_user_notice",
                                    _("Project Approved User Notice"),
                                    _("A project has been approved - user notice."),
                                    verbosity=verbosity)


def init_signals():
    post_save.connect(save_contribution, sender=Project, weak=False)
