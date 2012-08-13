def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.news.models import News
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=News, weak=False)