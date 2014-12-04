from django.template import Library


register = Library()


@register.inclusion_tag("resumes/options.html", takes_context=True)
def resume_options(context, user, resume):
    context.update({
        "opt_object": resume,
        "user": user
    })
    return context


@register.inclusion_tag("resumes/nav.html", takes_context=True)
def resume_nav(context, user, resume=None):
    context.update({
        'nav_object': resume,
        "user": user
    })
    return context


@register.inclusion_tag("resumes/search-form.html", takes_context=True)
def resume_search(context):
    return context


@register.inclusion_tag("resumes/top_nav_items.html", takes_context=True)
def resume_current_app(context, user, resume=None):
    context.update({
        "app_object": resume,
        "user": user
    })
    return context
