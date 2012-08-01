def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.architecture_projects.models import ArchitectureProject
    from tendenci.contrib.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=ArchitectureProject, weak=False)