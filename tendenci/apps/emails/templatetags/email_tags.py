from django.template import Library

from tendenci.apps.emails import footers

register = Library()


@register.inclusion_tag("emails/options.html", takes_context=True)
def emails_options(context, email):
    context.update({
        "opt_object": email,
    })
    return context


@register.inclusion_tag("emails/nav.html", takes_context=True)
def emails_nav(context, email=None):
    context.update({
        "nav_object": email,
    })
    return context


@register.inclusion_tag("emails/top_nav_items.html", takes_context=True)
def emails_current_app(context, email=None):
    context.update({
        "app_object": email,
    })
    return context


@register.simple_tag
def html_footer():
    """Make the HTML email footer available in templates."""
    return footers.html_footer()


@register.simple_tag
def text_footer():
    """Make the text email footer available in templates."""
    return footers.text_footer()
