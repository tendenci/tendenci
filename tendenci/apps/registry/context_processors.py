from tendenci.apps.registry.sites import site


def registered_apps(request):
    """
    Context processor to display registered apps

    {% for app in registered_apps %}
        {{ app }}
        {{ app.author }}
    {% endif %}

    {% for app in registered_apps.core %}
        {{ app }}
        {{ app.author }}
    {% endif %}
    """
    contexts = {}
    app_context = site.get_registered_apps()

    contexts['registered_apps'] = app_context

    return contexts


def enabled_addons(request):
    """
    Context processor that further filters registered apps
    by selecting only the enabled addons.

    """

    contexts = {}
    app_context = site.get_registered_apps()

    enabled_apps = []
    for app in app_context.addons:
        if app.get('enabled', False):
            enabled_apps.append(app)

    contexts['enabled_addons'] = enabled_apps

    return contexts
