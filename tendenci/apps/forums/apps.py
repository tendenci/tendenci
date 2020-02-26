# coding=utf-8

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PybbConfig(AppConfig):
    name = 'tendenci.apps.forums'
    verbose_name = _('Forums')

    def ready(self):
        from . import signals
        signals.setup()
