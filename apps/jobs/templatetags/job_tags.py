from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from jobs.models import Job

register = Library()


@register.inclusion_tag("jobs/options.html", takes_context=True)
def job_options(context, user, job):
    context.update({
        "opt_object": job,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/nav.html", takes_context=True)
def job_nav(context, user, job=None):
    context.update({
        'nav_object': job,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/search-form.html", takes_context=True)
def job_search(context):
    return context


@register.inclusion_tag("jobs/pricing-nav.html", takes_context=True)
def job_pricing_nav(context, user, job_pricing=None):
    context.update({
        'nav_object': job_pricing,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/pricing-options.html", takes_context=True)
def job_pricing_options(context, user, job_pricing):
    context.update({
        "opt_object": job_pricing,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/pricing-table.html", takes_context=True)
def job_pricing_table(context):
    from jobs.models import JobPricing
    job_pricings = JobPricing.objects.filter(status=1).order_by('duration')
    show_premium_price = False
    show_member_price = False
    premium_jp = JobPricing.objects.filter(status=1).filter(premium_price__gt=0)
    if premium_jp:
        show_premium_price = True
    member_jp = JobPricing.objects.filter(status=1).filter(regular_price_member__gt=0)
    if member_jp:
        show_member_price = True
    context.update({
        "job_pricings": job_pricings,
        'show_premium_price': show_premium_price,
        'show_member_price': show_member_price
    })
    return context


class ListJobNode(ListNode):
    model = Job


@register.tag
def list_jobs(parser, token):
    """
    Example:
        {% list_jobs as jobs_list [user=user limit=3 order"title" q="engineering"] %}
        {% for job in jobs_list %}
            {{ job.title }}
        {% endfor %}

    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-post_dt'

    return ListJobNode(context_var, *args, **kwargs)
