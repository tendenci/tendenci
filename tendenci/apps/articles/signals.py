from django.db.models.signals import post_save
from django.utils.translation import ugettext_noop as _

from tendenci.apps.notifications import models as notification
from tendenci.apps.articles.models import Article
from tendenci.apps.contributions.signals import save_contribution


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("article_added",
                                    _("Article Added"),
                                    _("An article has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("article_deleted",
                                    _("Article Deleted"),
                                    _("An article has been deleted"),
                                    verbosity=verbosity)


def init_signals():
    post_save.connect(save_contribution, sender=Article, weak=False)
