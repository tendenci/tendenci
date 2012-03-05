import haystack
from django.db.models.signals import post_save
from registry import site as registry_site
from search.signals import save_unindexed_item

haystack.autodiscover()

registered_apps = registry_site.get_registered_apps()
registered_apps_models = [app['model'] for app in registered_apps]

for app_model in registered_apps_models:
    post_save.connect(save_unindexed_item, sender=app_model, weak=False)
