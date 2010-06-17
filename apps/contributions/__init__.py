
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from contributions.models import Contribution

from articles.models import Article
from pages.models import Page
from news.models import News
from photos.models import PhotoSet, Image
from stories.models import Story
from files.models import File

def save_contribution(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)

    try: # record exists
        contrib = Contribution.objects.get(
            content_type = content_type,
            object_id = instance.pk)
    except: # create record
        contrib = Contribution()
        contrib.content_type = content_type
        contrib.object_id = instance.id
        contrib.creator = instance.owner

    title_attrs = (
        'title',
        'headline',
        'name',
    )
    for attr in title_attrs:
        if hasattr(instance, attr):
            contrib.title = getattr(instance, attr, '')
            break

    contrib.owner = instance.owner
    contrib.save()

post_save.connect(save_contribution, sender=Article, weak=False)
post_save.connect(save_contribution, sender=Page, weak=False)
post_save.connect(save_contribution, sender=News, weak=False)
post_save.connect(save_contribution, sender=PhotoSet, weak=False)
post_save.connect(save_contribution, sender=Image, weak=False)
post_save.connect(save_contribution, sender=Story, weak=False)
post_save.connect(save_contribution, sender=File, weak=False)