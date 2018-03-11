from django.template import Library, TemplateSyntaxError

from tendenci.apps.case_studies.models import CaseStudy
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs

register = Library()

@register.inclusion_tag("case_studies/top_nav_items.html", takes_context=True)
def case_study_current_app(context, user, case_study=None):
    context.update({
        "app_object": case_study,
        "user": user
    })
    return context

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
    perms = 'case_studies.view_casestudy'


@register.tag
def list_case_studies(parser, token):
    """
    Used to pull a list of :model:`case_studies.CaseStudy` items.

    Usage::

        {% list_case_studies as [varname] [options] %}

    Be sure the [varname] has a specific name like ``case_studies_sidebar`` or
    ``case_studies_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Added**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_case_studies as case_studies_list limit=5 tags="cool" %}
        {% for cs in case_studies_list %}
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
