from __future__ import absolute_import
from django import VERSION

if VERSION[:2] < (1, 7):
    from . import signals
    signals.setup()
else:
    default_app_config = 'tendenci.apps.forums.apps.PybbConfig'
