import simplejson

from django.template import Library

from tendenci.apps.dashboard.models import DashboardStat
register = Library()


@register.inclusion_tag("dashboard/nav.html", takes_context=True)
def dashboard_nav(context, user):
    context.update({
        "user": user
    })
    return context


@register.inclusion_tag("dashboard/stats.html", takes_context=True)
def dashboard_stat(context, stat_type):
    value = ''
    type_name = ''
    label = ''
    stat = DashboardStat.objects.get_latest(stat_type)
    if stat:
        value = simplejson.loads(stat.value, use_decimal=True)
        type_name = stat_type.name
        label = stat_type.description
    context.update({
        "type_name": type_name,
        "label": label,
        "value": value,
    })
    return context
