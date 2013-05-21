from django.core.cache import cache
from django.conf import settings

non_model_event_logs = {
    'rss': {
        'feed_base':('630000', '00FF00'), # rss feed base
        'global_feed':('630500', '00FF00'), # global rss feed
        'article_feed':('630543', '00FF33'), # articles rss feed
        'news_feed':('630530', '00FFCC'), # news rss feed
        'pages_feed':('630560', '33FF99'), # pages rss feed
        'jobs_feed':('630525', '00FF99'), # jobs rss feed
    },
    'homepage':{
        'view':('100000', '17ABB9'), # base app
    }
}

def generate_colors():
    """Create the event id to color dict so we won't
    have to iterate over the apps in the event registry
    for every event id.
    """
    from tendenci.core.registry import site
    d = {}
    apps = site.get_registered_apps().all_apps
    for app in apps:
        if 'event_logs' in app:
            for model in app['event_logs'].keys():
                for event in app['event_logs'][model].keys():
                    log_id = app['event_logs'][model][event][0]
                    color = app['event_logs'][model][event][1]
                    d[log_id] = color
    return d
    
def generate_base_colors():
    """Crete the event id to color dict for event logs that
    are not associated with any model or registry.
    """
    d = {}
    for model in non_model_event_logs.keys():
        for event in non_model_event_logs[model].keys():
            log_id = non_model_event_logs[model][event][0]
            color = non_model_event_logs[model][event][1]
            d[log_id] = color
    return d

def cache_colors(colors):
    keys = [settings.CACHE_PRE_KEY, 'event_log_colors']
    key = '.'.join(keys)
    is_set = cache.add(key, colors)
    if not is_set:
        cache.set(key, colors)

def get_color(event_id):
    """Gets the hex color of an event log based on the event id
    get_color('id')
    """
    keys = [settings.CACHE_PRE_KEY, 'event_log_colors']
    key = '.'.join(keys)
    colors = cache.get(key)
    if not colors:
        colors = generate_colors()
        colors.update(generate_base_colors())
        cache_colors(colors)

    if event_id in colors:
        print event_id
        return colors[event_id]
    else:
        return '17ABB9'

    return ''
