from django.template import Library, TemplateSyntaxError

from tendenci.apps.chapters.models import Chapter
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListChaptersNode(ListNode):
    model = Chapter
    perms = 'chapters.view_chapter'

@register.inclusion_tag("chapters/nav.html", takes_context=True)
def chapter_nav(context, user, chapter=None):
    context.update({
        'nav_object': chapter,
        "user": user
    })
    return context


@register.inclusion_tag("chapters/top_nav_items.html", takes_context=True)
def chapter_current_app(context, user, chapter=None):
    context.update({
        "app_object": chapter,
        "user": user
    })
    return context


@register.tag
def list_chapters(parser, token):
    """
    Example::

        {% list_chapters as chapters_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
        {% for chapter in chapters %}
            {{ chapter.something }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListChaptersNode(context_var, *args, **kwargs)

@register.inclusion_tag("chapters/search-form.html", takes_context=True)
def chapter_search(context):
    return context

@register.inclusion_tag("chapters/options.html", takes_context=True)
def chapter_options(context, user, chapter):
    context.update({
        "opt_object": chapter,
        "user": user
    })
    return context

@register.inclusion_tag("chapters/form.html", takes_context=True)
def chapter_form(context, form, formset=None):
    context.update({
        'form': form,
        'formset': formset
    })
    return context

@register.inclusion_tag("chapters/officer-formset.html", takes_context=True)
def chapter_officer_formset(context, formset):
    context.update({
        'formset': formset
    })
    return context
