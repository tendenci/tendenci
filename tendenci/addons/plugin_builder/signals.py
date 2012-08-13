def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.plugin_builder.models import Plugin
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Plugin, weak=False)