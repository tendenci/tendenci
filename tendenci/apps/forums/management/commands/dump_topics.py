#!/usr/bin/env python
# vim:fileencoding=utf-8
from __future__ import unicode_literals
__author__ = 'zeus'

from django.core.management.base import BaseCommand
from tendenci.apps.forums.models import Topic, Post
from django.core import serializers


class Command(BaseCommand):
    args = '<topic_id topic_id>'
    help = 'Dump target topics to json'

    def handle(self, *args, **options):
        ids = [int(topic_id) for topic_id in args]
        objects = list(Topic.objects.filter(id__in=ids)) + list(Post.objects.filter(topic_id__in=ids))
        dump = serializers.serialize('json', objects)
        self.stdout.write(dump)
