from django.core.cache import cache

base_colors = {
     # contacts - TEAL/LIME-GREEN base
    '125114':'33CCCC', # add - contact form submitted / new user added
    '125115':'0066CC', # add - contact form submitted / user already exists
    
    # entities - TURQUOISE base - complement is ?????
    '290000':'00FFCC', # base
    '291000':'00FFCC', # add
    '292000':'33FFCC', # edit
    '293000':'33FF66', # delete
    '294000':'66FFCC', # search 
    '295000':'99FFCC', # view

    # accounting
    '310000':'006666', # base
    '311000':'006666', # add
    '312000':'006633', # edit
    '313000':'006600', # delete
    '314000':'009900', # search 
    '315000':'009933', # view 
    '311220':'FF0000', # invoice adjusted    RED!!! 
    '312100':'339900', # general ledger added 
    '312200':'339900', # general ledger edited
    '312300':'339900', # general ledger deleted
    '312400':'339900', # general ledger searched
    '312500':'339900', # general ledger viewed
    '313300':'669933', # accounting entry deleted
    '313400':'669933', # accounting transaction deleted
    '315105':'669933', # acct entry table export    

    # payments - PINK ORANGE base - complement is ????
    '280000':'FF6666', # base
    '281000':'FF6666', # add
    '282000':'FF6666', # edit
    '283000':'FF6666', # delete
    '284000':'FF6666', # search 
    '285000':'FF6666', # view 
    '286000':'FF6666', # export 
    '282101':'FF6666', # Edit - Credit card approved 
    '282102':'FF6666', # Edit - Credit card declined 

    # make_payments - PINK ORANGE base - complement is ????
    '670000':'66CC00', # base
    '671000':'66CC00', # add
    '672000':'66CC33', # edit
    '673000':'66CC66', # delete
    '674000':'66FF00', # search 
    '675000':'66FF33', # view 
   
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
