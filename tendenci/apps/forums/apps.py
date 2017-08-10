# coding=utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PybbConfig(AppConfig):
    name = 'tendenci.apps.forums'
    verbose_name = _('Forums')

    def ready(self):
        from . import signals
        signals.setup()
