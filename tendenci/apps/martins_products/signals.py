def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.martins_products.models import Product
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Product, weak=False)