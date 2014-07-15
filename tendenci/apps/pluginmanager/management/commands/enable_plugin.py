from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, plugin_name, **options):
        """
        Add a plugin and activate it.
        """
        from tendenci.apps.pluginmanager.models import PluginApp

        # strip out the 'plugins.' if it is in there
        plugin_name = plugin_name.replace("plugins.","")

        try:
            __import__("plugins.%s" % plugin_name)
            try:
                plugin = PluginApp.objects.get(
                        title=plugin_name,
                        package=".".join(["plugins",plugin_name]),
                    )
                plugin.is_enabled = True
                plugin.is_installed = True
                plugin.save()
                print "The plugin %s existed. It has been enabled." % plugin_name
            except:
                plugin = PluginApp.objects.create(
                        title=plugin_name,
                        package=".".join(["plugins",plugin_name]),
                        description=plugin_name,
                        is_installed=True,
                        is_enabled=True
                    )
                print "New plugin %s installed and enabled." % plugin_name
        except ImportError:
            print "No plugin %s found." % plugin_name
