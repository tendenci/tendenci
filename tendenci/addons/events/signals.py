def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.events.models import Event
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Event, weak=False)