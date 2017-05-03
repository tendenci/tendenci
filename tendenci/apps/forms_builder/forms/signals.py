def init_signals():
    from django.db.models.signals import post_save
    from tendenci.apps.forms_builder.forms.models import FormEntry
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=FormEntry, weak=False)
