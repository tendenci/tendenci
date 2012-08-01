def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.courses.models import Course
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Course, weak=False)