from datetime import date, timedelta
from django.utils.datastructures import SortedDict

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

#TODO: this is just temporary colors for event summary reports
#      should be replaced with some database values that currently unclear
COLORS = {
    'articles': '#660000',
    'auth': '#FFCC00',
    'contacts': '#009900',
    'entities': '#009999',
    'locations': '#0099FF',
    'news': '#0000FF',
    'pages': '#9900CC',
    'photos': '#FF99FF',
    'profiles': '#666699',
    'stories': '#CCCC99',
    'user_groups': '#000000',
}

def append_colors(data):
    for item in data:
        item['color'] = COLORS.get(item['source'], '#CCCCCC')

def day_bars(data, year, month, height=300, add_coloring=True):
    "Returns bars prepared for event-summary chart"
    
    def _sum_counts(items):
        for values in items.values():
            yield sum([i['count'] for i in values])
    
    if add_coloring:
        append_colors(data)
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
            #item['color'] = COLORS.get(item['source'], '#CCCCCC')
    return result
