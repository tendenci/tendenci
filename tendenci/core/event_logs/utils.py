from datetime import date, timedelta
from django.utils.datastructures import SortedDict
from django.conf import settings

app_exclude_list = [
        u'announcements',
        u'campaign_monitor',
        u'careers',
        u'educations',
        u'social_auth',
        u'social_media',
        u'contributions',
        u'notifications',
        u'pluginmanager',
        u'redirect',
        u'registration',
        u'reports',
        u'api',
        u'api_tasty',
        u'categories',
        u'custom_storages',
        u'event_logs',
        u'meta',
        u'mobile',
        u'newsletters',
        u'perms',
        u'registry',
        u'robots',
        u'rss',
        u'sitemaps',
        u'tags',
        u'theme',
        u'versions',
        u'events.ics',
        u'model_report',
        u'libs.model_report',
        u'libs.styled_forms',
    ]

remove_list = [
        'tendenci',
        'models',
        'views',
        'addons',
        'core',
        'apps',
        'contrib'
        ]

def month_days(year, month):
    "Returns iterator for days in selected month"
    day = date(year, month, 1)
    while day.month == month:
        yield day
        day += timedelta(days=1) 

def request_month_range(request):
    "returns month start date and end date"
    now = date.today()
    year = int(request.GET.get('year') or str(now.year))
    month = int(request.GET.get('month') or str(now.month))
    days = list(month_days(year, month)) 
    return days[0], days[-1]


def day_bars(data, year, month, height, color_func=None):
    "Returns bars prepared for event-summary chart"
    
    def _sum_counts(items):
        for values in items.values():
            yield sum([i['count'] for i in values])
    
    if color_func:
        color_func(data)
    result = SortedDict([(d, []) for d in month_days(year, month)])
    for item in data:
        result[item['day']].append(item)
    try:
        kH = height*1.0 / max(_sum_counts(result))
    except Exception:
        kH = 1.0
    for values in result.values():
        for item in values:
            item['height'] = int(item['count']*kH)
    return result


def get_app_list_choices():
    app_list = []
    for app in settings.INSTALLED_APPS:
        if 'tendenci' in app or 'addons' in app:
            application = app.split('.')
            for item in remove_list:
                if item in application:
                    application.remove(item)

            app_name = ".".join(application)
            if app_name == 'base':
                app_name = 'homepage'

            if not app_name in app_exclude_list:
                app_list.append(app_name)

    app_list.append('django.auth')
    app_list.append('django.admin')
    app_list = sorted(app_list)
    app_choices = [(i, i) for i in app_list]
    app_choices = [('', '----------')] + app_choices

    return app_choices
