def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.quotes.models import Quote
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Quote, weak=False)