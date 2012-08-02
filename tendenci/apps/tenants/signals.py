def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.tenants.models import Tenant
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Tenant, weak=False)