def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.recurring_payments.models import RecurringPayment
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=RecurringPayment, weak=False)
