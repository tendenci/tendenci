from __future__ import print_function
import os
from optparse import make_option
from boto.s3.connection import S3Connection

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError


addons_list = [
    'events', 'jobs', 'memberships', 'directories', 'articles',
    'news', 'photos'
]

apps_list = [
    'boxes', 'entities', 'navs', 'pages',
    'profiles', 'stories', 'user_groups'
]

cores_list = [
    'files'
]


class Command(BaseCommand):
    help = "Remove non-profit-organization default data"

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        module = None
        if len(args) == 1:
            module = args[0]
        elif len(args) > 0:
            raise CommandError('Command accepts 1 arguement (%d given)' % len(args))

        accepted_modules = addons_list + apps_list + cores_list
        if module and module not in accepted_modules:
            raise CommandError('Invalid module. accepted arguments are %s' % accepted_modules )
        self.removedata(module)

    def removedata(self, module):
        modules_list = []

        for addon in addons_list:
            if module is None or module == addon:
                modules_list.append( "tendenci.apps.%s.models" % addon )

        for app in apps_list:
            if module is None or module == app:
                modules_list.append( "tendenci.apps.%s.models" % app )

        for core in cores_list:
            if module is None or module == core:
                modules_list.append( "tendenci.apps.%s.models" % core )


        contenttypes = ContentType.objects.all()

        for module in modules_list:
            self.delete_module(module, contenttypes)

    def delete_module(self, module, contenttypes):
        for ct in contenttypes:
            m = ct.model_class()
            if m.__module__ == module:
                try:
                    instances = m.objects.filter(tags__contains='tendencidemo')
                    print("module -- %s %s" % (m.__module__, m.__name__))
                    for instance in instances:
                        if instance.owner == instance.creator:
                            print("%s -- %s" % (m.__name__, instance))
                            links = [rel.get_accessor_name() for rel in instance._meta.get_all_related_objects()]
                            print("looking at related objects...")
                            for link in links:
                                try:
                                    objects = getattr(instance, link).all()
                                    for obj in objects:
                                        print("deleting %s" % obj)
                                        obj.delete()
                                except Exception:
                                    pass

                            print("deleting %s -- %s" % (m.__name__, instance))
                            instance.delete()
                    print("")
                    print("")
                except FieldError:
                    pass # model has no tag field
                except Exception:
                    print("Error in deleting %s -- %s" % (m.__module__, m.__name__))
                    import sys, traceback
                    traceback.print_exc(file=sys.stdout)
                    pass


