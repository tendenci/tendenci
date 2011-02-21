from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from case_studies.models import CaseStudy
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


@register.inclusion_tag("case_studies/options.html", takes_context=True)
def case_study_options(context, user, case_study):
    context.update({
        "opt_object": case_study,
        "user": user
    })
    return context


@register.inclusion_tag("case_studies/search-form.html", takes_context=True)
def case_study_search(context):
    return context


class ListCaseStudyNode(ListNode):
    model = CaseStudy


@register.tag
def list_case_studies(parser, token):
    """
    Example:

    {% list_case_studies as the_case_studies user=user limit=3 %}
    {% for cs in the_case_studies %}
        {{ cs.client }}
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
        kwargs['order'] = '-create_dt'

    return ListCaseStudyNode(context_var, *args, **kwargs)
