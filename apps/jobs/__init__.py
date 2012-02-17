from django.db.models.signals import post_save
from jobs.models import Job
from contributions.signals import save_contribution

post_save.connect(save_contribution, sender=Job, weak=False)