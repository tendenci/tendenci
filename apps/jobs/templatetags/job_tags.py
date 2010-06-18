from django.template import Library

register = Library()

@register.inclusion_tag("jobs/options.html", takes_context=True)
def job_options(context, user, job):
    context.update({
        "job": job,
        "user": user
    })
    return context

@register.inclusion_tag("jobs/nav.html", takes_context=True)
def job_nav(context, user):
    context.update({
        "user": user
    })
    return context

@register.inclusion_tag("jobs/search-form.html", takes_context=True)
def job_search(context):
    return context