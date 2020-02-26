#!/usr/bin/env python
# vim:fileencoding=utf-8



from django.core.management.base import BaseCommand
from tendenci.apps.forums.models import Topic, Forum

class Command(BaseCommand):
    help = 'Recalc post counters for forums and topics'

    def handle(self, *args, **options):

        for topic in Topic.objects.all():
            topic.update_counters()
            self.stdout.write('Successfully updated topic "%s"\n' % topic)

        for forum in Forum.objects.all():
            forum.update_counters()
            self.stdout.write('Successfully updated forum "%s"\n' % forum)
