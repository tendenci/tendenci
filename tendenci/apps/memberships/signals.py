
def init_signals():
    from django.db.models.signals import post_save, post_delete
    from tendenci.apps.memberships.models import MembershipDefault, MembershipApp
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=MembershipDefault, weak=False)
    post_delete.connect(update_membs_app_id, sender=MembershipApp, weak=False)
    post_save.connect(check_and_update_membs_app_id, sender=MembershipApp, weak=False)
    

def check_and_update_membs_app_id(sender, **kwargs):
    my_app = kwargs['instance']

    if not my_app.status:
        switch_memberships_app_id(my_app)


def update_membs_app_id(sender, **kwargs):
    app_to_be_deleted = kwargs['instance']
    switch_memberships_app_id(app_to_be_deleted)

       
def switch_memberships_app_id(app_from):
    from tendenci.apps.memberships.models import MembershipDefault, MembershipApp
    # each membership has an app_id associated.
    # since this app is to be deleted, we need to update memberships
    # with an available app_id
    app = MembershipApp.objects.exclude(id=app_from.id)
    if app_from.use_for_corp:
        app = app.filter(use_for_corp=True)
    app = app.filter(status=True, status_detail__in=('published', 'active'))
    [app] = app.order_by('-id')[:1] or [None]

    if app:
        MembershipDefault.objects.filter(app_id=app_from.id).update(app=app)