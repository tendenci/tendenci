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
