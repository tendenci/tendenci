from django.utils.translation import gettext_noop as _
from tendenci.apps.notifications import models as notification


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("directory_added",
                                    _("Directory Added"),
                                    _("A directory has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("directory_approved_user_notice",
                                    _("Directory Approved User Notice"),
                                    _("A directory has been approved - user notice."),
                                    verbosity=verbosity)
    notification.create_notice_type("directory_deleted",
                                    _("Directory Deleted"),
                                    _("A directory has been deleted"),
                                    verbosity=verbosity)
    notification.create_notice_type("directory_renewed",
                                    _("Directory Renewed"),
                                    _("A directory has been renewed"),
                                    verbosity=verbosity)
    notification.create_notice_type("directory_renewal_eligible",
                                    _("Directory Eligible for Renewal"),
                                    _("A directory is eligible for renewal"),
                                    verbosity=verbosity)
    notification.create_notice_type("affiliate_requested_to_owner",
                                    _("Affiliation Request Submitted Owner Notice"),
                                    _("An affiliation request has been submitted - owner notice"),
                                    verbosity=verbosity)
    notification.create_notice_type("affiliate_requested_to_submitter",
                                    _("Affiliation Request Submitted Submitter Notice"),
                                    _("An affiliation request has been submitted - submitter notice"),
                                    verbosity=verbosity)
    notification.create_notice_type("affiliate_approved_to_submitter",
                                    _("Affiliation Request Approved Submitter Notice"),
                                    _("An affiliation request has been approved - submitter notice"),
                                    verbosity=verbosity)
    notification.create_notice_type("affiliate_rejected_to_submitter",
                                    _("Affiliation Request Rejected Submitter Notice"),
                                    _("An affiliation request has been rejected - submitter notice"),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.directories.models import Directory
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Directory, weak=False)
