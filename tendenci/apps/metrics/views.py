import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Avg, Max, Min, Count, Sum

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.base.http import Http403
from tendenci.apps.metrics.models import Metric


@login_required
def index(request, template_name="metrics/index.html"):

    if not request.user.profile.is_superuser:
        raise Http403

    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    last_week = Metric.objects.filter(create_dt__gte=seven_days_ago)
    try:
        yesterday = Metric.objects.all().order_by('-create_dt')[0]
    except:
        yesterday = None
    week_sums = last_week.aggregate(total_visits=Sum('visits'))
    month_sums = Metric.objects.filter(create_dt__gte=one_month_ago).aggregate(total_visits=Sum('visits'))

    EventLog.objects.log()

    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))
