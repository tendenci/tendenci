def init_signals():
    from django.db.models.signals import post_save, post_delete
    from tendenci.addons.corporate_memberships.models import CorpMembership
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=CorpMembership, weak=False)
