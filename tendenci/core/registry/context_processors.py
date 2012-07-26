from tendenci.core.registry import site


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
