from django.db import models
from django.db.models.signals import post_save


class PluginApp(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    package = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True, blank=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = self.package.replace('tendenci.', '').replace('addons.', '').replace('_', ' ').title()
        return super(PluginApp, self).save(*args, **kwargs)


###
# Tools
def db2json():
    from django.utils import simplejson
    import os
    from django.conf import settings
    path = settings.PROJECT_ROOT
    plugins = list(PluginApp.objects.all().values('id', 'title', 'package', 'is_enabled'))
    data = simplejson.dumps(plugins, indent=1)
    f = open(os.path.join(path, 'addons_list.json'), 'w')
    f.write(data)
    f.close()


def _update_apps(instance=None, created=False):
    from django.core.management import call_command
    try:
        call_command('touch_settings')
    except:
        pass


def post_save_pluginapp(sender, instance=None, created=False, **kwargs):
    _update_apps(instance=instance, created=created)

post_save.connect(post_save_pluginapp, sender=PluginApp)
