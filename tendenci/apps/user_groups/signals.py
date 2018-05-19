from django.db.models.signals import post_delete
from django.utils.translation import ugettext_noop as _
from tendenci.apps.notifications import models as notification


def create_notice_types(sender, **kwargs):
    verbosity = kwargs.get('verbosity', 2)
    notification.create_notice_type("group_added",
                                    _("Group Added"),
                                    _("A group has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("group_deleted",
                                    _("Group Deleted"),
                                    _("A group has been deleted"),
                                    verbosity=verbosity)
   

def init_signals():
    from tendenci.apps.user_groups.models import Group

    def delete_auth_group(sender, **kwargs):
        group = kwargs['instance']
        auth_group = group.group
        if auth_group:
            auth_group.delete()

    post_delete.connect(delete_auth_group, sender=Group, weak=False)
