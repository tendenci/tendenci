from django.template import Library

register = Library()

@register.inclusion_tag("email_blocks/options.html", takes_context=True)
def email_block_options(context, email_block):
    context.update({
        "opt_object": email_block,
    })
    return context

@register.inclusion_tag("email_blocks/nav.html", takes_context=True)
def email_blocks_nav(context, email_block=None):
    context.update({
        "nav_object": email_block,
    })
    return context
