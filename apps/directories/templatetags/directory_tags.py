from django.template import Library

register = Library()

@register.inclusion_tag("directories/options.html", takes_context=True)
def directory_options(context, user, directory):
    context.update({
        "opt_object": directory,
        "user": user
    })
    return context

@register.inclusion_tag("directories/nav.html", takes_context=True)
def directory_nav(context, user, directory=None):
    context.update({
        "nav_object" : directory,
        "user": user
    })
    return context

@register.inclusion_tag("directories/search-form.html", takes_context=True)
def directory_search(context):
    return context


@register.inclusion_tag("directories/pricing-nav.html", takes_context=True)
def directory_pricing_nav(context, user, directory_pricing=None):
    context.update({
        'nav_object': directory_pricing,
        "user": user
    })
    return context

@register.inclusion_tag("directories/pricing-options.html", takes_context=True)
def directory_pricing_options(context, user, directory_pricing):
    context.update({
        "opt_object": directory_pricing,
        "user": user
    })
    return context

@register.inclusion_tag("directories/pricing-table.html", takes_context=True)
def directory_pricing_table(context):
    from directories.models import DirectoryPricing
    directory_pricings =DirectoryPricing.objects.filter(status=1).order_by('duration')
    show_premium_price = False
    premium_jp = DirectoryPricing.objects.filter(status=1).filter(premium_price__gt=0)
    if premium_jp:
        show_premium_price = True
    context.update({
        "directory_pricings": directory_pricings,
        'show_premium_price': show_premium_price
    })
    return context