from django.db.models.signals import post_delete


def init_signals():
    from tendenci.apps.user_groups.models import Group

    def delete_auth_group(sender, **kwargs):
        group = kwargs['instance']
        auth_group = group.group
        if auth_group:
            auth_group.delete()

    post_delete.connect(delete_auth_group, sender=Group, weak=False)
