from django.template import Library

register = Library()

@register.inclusion_tag("stories/options.html", takes_context=True)
def stories_options(context, user, story):
    context.update({
        "story_this": story,
        "user_current": user,
    })
    return context

@register.inclusion_tag("stories/nav.html", takes_context=True)
def stories_nav(context, user, story=None):
    context.update({
        "story_this": story,
        "user_current": user,
    })
    print context["story_this"]
    return context

@register.inclusion_tag("stories/search-form.html", takes_context=True)
def stories_search(context):
    return context