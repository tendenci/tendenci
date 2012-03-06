from django.core.cache import cache

base_colors = {
   
    # actions (Marketing Actions)
    '300000':'FF0033', # base
    '301000':'FF0033', # add
    '301100':'FF3333', # edit
    '303000':'FF0033', # delete
    '304000':'FF0033', # search 
    '305000':'FF0066', # view
    '301001':'FF0033', # submitted
    '301005':'FF0099', # resend

    # emails
    '130000':'CC3300', # base
    '131000':'CC3300', # add
    '132000':'CC3300', # edit
    '133000':'CC3300', # delete
    '134000':'CC3300', # search 
    '135000':'CC3300', # view
    '131100':'CC3366', # email send failure
    '131101':'CC3399', # email send success
    '131102':'CC33CC', # email send success - newsletter
    '130999':'FF0000', # email SPAM DETECTED!! (RED - this is important)

    # email_blocks
    '135000':'CC3300', # base
    '135100':'CC3300', # add
    '135300':'CC3300', # edit
    '135300':'CC3300', # delete
    '135400':'CC3300', # search 
    '135550':'CC3300', # view

    # rss
    '630000':'00FF00', # rss feed base
    '630500':'00FF00', # global rss feed
    '630543':'00FF33', # articles rss feed
    '630530':'00FFCC', # news rss feed
    '630560':'33FF99', # pages rss feed
    '630525':'00FF99', # jobs rss feed 
    
    # recurring payments - green
    '1120000':'1A7731', #base
    '1120100':'14A037', # add
    '1120200':'478256', # edit
    '1120300':'8FBA9A', # delete
    '1120400':'14E548', # search
    '1120500':'339B41', # disable

    # tendenci_guide
    '1002000':'A20900', # base
    '1002100':'119933', # add
    '1002200':'EEDD55', # edit
    '1002300':'AA2222', # delete
    '1002400':'CC55EE', # search
    '1002500':'55AACC', # detail
    
}

def generate_colors():
    """Create the event id to color dict so we won't
    have to iterate over the apps in the event registry
    for every event id.
    """
    from registry import site
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

def cache_colors(colors):
    key = 'event_log_colors'
    is_set = cache.add(key, colors)
    if not is_set:
        cache.set(key, colors)

def get_color(event_id):
    """Gets the hex color of an event log based on the event id
    get_color('id')
    """
    key = 'event_log_colors'
    colors = cache.get(key)
    if not colors:
        colors = generate_colors()
        colors.update(base_colors)
        cache_colors(colors)
    
    if event_id in colors:
        return colors[event_id]
    else:
        return 'FFFFFF'
    
    return ''
