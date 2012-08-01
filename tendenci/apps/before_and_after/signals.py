def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.before_and_after.models import BeforeAndAfter
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=BeforeAndAfter, weak=False)