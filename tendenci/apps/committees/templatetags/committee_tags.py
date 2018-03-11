from django.template import Library, TemplateSyntaxError

from tendenci.apps.committees.models import Committee
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListCommitteesNode(ListNode):
    model = Committee
    perms = 'committees.view_committee'

@register.inclusion_tag("committees/nav.html", takes_context=True)
def committee_nav(context, user, committee=None):
    context.update({
        'nav_object': committee,
        "user": user
    })
    return context


@register.inclusion_tag("committees/top_nav_items.html", takes_context=True)
def committee_current_app(context, user, committee=None):
    context.update({
        "app_object": committee,
        "user": user
    })
    return context


@register.tag
def list_committees(parser, token):
    """
    Example::

        {% list_committees as committees_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
        {% for committee in committees %}
            {{ committee.something }}
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

    return ListCommitteesNode(context_var, *args, **kwargs)

@register.inclusion_tag("committees/search-form.html", takes_context=True)
def committee_search(context):
    return context

@register.inclusion_tag("committees/options.html", takes_context=True)
def committee_options(context, user, committee):
    context.update({
        "opt_object": committee,
        "user": user
    })
    return context

@register.inclusion_tag("committees/form.html", takes_context=True)
def committee_form(context, form, formset=None):
    context.update({
        'form': form,
        'formset': formset
    })
    return context

@register.inclusion_tag("committees/officer-formset.html", takes_context=True)
def committee_officer_formset(context, formset):
    context.update({
        'formset': formset
    })
    return context
