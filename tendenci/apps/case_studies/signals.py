def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.case_studies.models import CaseStudy
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=CaseStudy, weak=False)
