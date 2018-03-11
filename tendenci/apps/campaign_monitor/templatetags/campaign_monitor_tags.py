from django.template import Library
from django.conf import settings

register = Library()

@register.inclusion_tag("campaign_monitor/templates/options.html", takes_context=True)
def template_options(context, user, template):
    context.update({
        "opt_object": template,
        "user": user,
        "cm_url": settings.CAMPAIGNMONITOR_URL,
    })
    return context


@register.inclusion_tag("campaign_monitor/templates/nav.html", takes_context=True)
def template_nav(context, user, template=None):
    context.update({
        "nav_object": template,
        "user": user,
        "cm_url": settings.CAMPAIGNMONITOR_URL,
    })
    return context

@register.inclusion_tag("campaign_monitor/campaigns/options.html", takes_context=True)
def campaign_options(context, user, campaign):
    context.update({
        "opt_object": campaign,
        "user": user,
        "cm_url": settings.CAMPAIGNMONITOR_URL,
    })
    return context


@register.inclusion_tag("campaign_monitor/campaigns/nav.html", takes_context=True)
def campaign_nav(context, user, campaign=None):
    context.update({
        "nav_object": campaign,
        "user": user,
        "cm_url": settings.CAMPAIGNMONITOR_URL,
    })
    return context
