from django.template import Library

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