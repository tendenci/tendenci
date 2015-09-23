def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.staff.models import Staff
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Staff, weak=False)
