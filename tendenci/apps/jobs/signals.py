def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.jobs.models import Job
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Job, weak=False)