from django.utils.translation import gettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("video_added",
                                    _("Video Added"),
                                    _("A video has been added."),
                                    verbosity=verbosity)


def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.videos.models import Video
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Video, weak=False)
