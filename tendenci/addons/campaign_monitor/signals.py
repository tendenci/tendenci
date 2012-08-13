def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.campaign_monitor.models import Campaign
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Campaign, weak=False)