def init_signals():
    from django.db.models.signals import post_save
    from .models import Product
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Product, weak=False)