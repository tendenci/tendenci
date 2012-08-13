def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.make_payments.models import MakePayment
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=MakePayment, weak=False)