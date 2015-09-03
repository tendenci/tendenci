from django import VERSION

if VERSION[:2] < (1, 7):
    import signals
    signals.setup()
else:
    default_app_config = 'tendenci.apps.forums.apps.PybbConfig'
