from django.template import Node, Library, TemplateSyntaxError, Variable

from tendenci.apps.studygroups.models import StudyGroup
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListStudyGroupsNode(ListNode):
    model = StudyGroup
    perms = 'studygroups.view_studygroup'

@register.inclusion_tag("studygroups/nav.html", takes_context=True)
def studygroup_nav(context, user, study_group=None):
    context.update({
        'nav_object': study_group,
        "user": user
    })
    return context


@register.inclusion_tag("studygroups/top_nav_items.html", takes_context=True)
def studygroup_current_app(context, user, study_group=None):
    context.update({
        'app_object': study_group,
        "user": user
    })
    return context


@register.tag
def list_studygroups(parser, token):
    """
    Example::

        {% list_studygroups as studygroups_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
        {% for studygroup in studygroups %}
            {{ studygroup.something }}
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

    return ListStudyGroupsNode(context_var, *args, **kwargs)

@register.inclusion_tag("studygroups/search-form.html", takes_context=True)
def studygroup_search(context):
    return context

@register.inclusion_tag("studygroups/options.html", takes_context=True)
def studygroup_options(context, user, study_group):
    context.update({
        "opt_object": study_group,
        "user": user
    })
    return context

@register.inclusion_tag("studygroups/form.html", takes_context=True)
def studygroup_form(context, form, formset=None):
    context.update({
        'form': form,
        'formset': formset
    })
    return context

@register.inclusion_tag("studygroups/officer-formset.html", takes_context=True)
def studygroup_officer_formset(context, formset):
    context.update({
        'formset': formset
    })
    return context
