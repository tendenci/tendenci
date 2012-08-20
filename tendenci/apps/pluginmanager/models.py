from django.db import models
from django.utils.encoding import smart_str
from tendenci.core.perms.utils import update_admin_group_perms


class PluginApp(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    package = models.CharField(max_length=255)
    is_installed = models.BooleanField(default=True, blank=True)
    is_enabled = models.BooleanField(default=True, blank=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = self.package.replace('tendenci.', '').replace('addons.', '').replace('_', ' ').title()
        return super(PluginApp, self).save(*args, **kwargs)

###
# Signals
from django.core.management import call_command
post_save = models.signals.post_save
post_delete = models.signals.post_delete


def _update_apps(instance=None, created=False):
    db2json()
    from django.conf import settings
    from django.db.models.loading import cache as app_cache
    from tendenci.apps.pluginmanager import plugin_apps
    settings.INSTALLED_APPS = plugin_apps(settings.DEFAULT_INSTALLED_APPS, settings.PROJECT_ROOT)
    app_cache.loaded = False  # clear cache

    call_command('syncdb', interactive=False, migrate_all=False)
    call_command('migrate', interacte=False)
    call_command('touch_settings')
    # update the site settings (in database) if any
    if instance:
        print instance
        call_command('update_settings', smart_str(instance.package))


def post_save_pluginapp(sender, instance=None, created=False, **kwargs):
    _update_apps(instance=instance, created=created)
    # assign permission to the admin auth group
    update_admin_group_perms()

post_save.connect(post_save_pluginapp, sender=PluginApp)


def post_del_pluginapp(sender, **kwargs):
    _update_apps()
post_delete.connect(post_del_pluginapp, sender=PluginApp)

###
# Tools
from django.utils import simplejson
import os


def db2json():
    #path = os.path.abspath(os.path.dirname(__file__))
    from django.conf import settings
    path = settings.PROJECT_ROOT
    plugins = list(PluginApp.objects.all().values('id', 'title', 'package', 'is_enabled', 'is_installed'))
    data = simplejson.dumps(plugins, indent=1)
    f = open(os.path.join(path, 'plugins_list.json'), 'w')
    f.write(data)
    f.close()
