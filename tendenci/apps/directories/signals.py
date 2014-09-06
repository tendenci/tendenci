def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.directories.models import Directory
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Directory, weak=False)