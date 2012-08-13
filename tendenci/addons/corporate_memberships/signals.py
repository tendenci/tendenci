def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.corporate_memberships.models import CorporateMembership
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=CorporateMembership, weak=False)