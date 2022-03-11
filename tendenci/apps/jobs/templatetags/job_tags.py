from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.template import Library, TemplateSyntaxError, Variable
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

from tendenci.apps.jobs.models import Job
from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.perms.utils import get_query_filters


register = Library()


@register.inclusion_tag("jobs/options.html", takes_context=True)
def job_options(context, user, job):
    context.update({
        "opt_object": job,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/nav.html", takes_context=True)
def job_nav(context, user, job=None):
    context.update({
        'nav_object': job,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/search-form.html", takes_context=True)
def job_search(context):
    return context


@register.inclusion_tag("jobs/top_nav_items.html", takes_context=True)
def job_current_app(context, user, job=None):
    context.update({
        "app_object": job,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/search-form.html", takes_context=True)
def my_job_search(context):
    context.update({
        'my_job': True
    })
    return context


@register.inclusion_tag("jobs/pricing-nav.html", takes_context=True)
def job_pricing_nav(context, user, job_pricing=None):
    context.update({
        'nav_object': job_pricing,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/pricing-options.html", takes_context=True)
def job_pricing_options(context, user, job_pricing):
    context.update({
        "opt_object": job_pricing,
        "user": user
    })
    return context


@register.inclusion_tag("jobs/pricing-table.html", takes_context=True)
def job_pricing_table(context):
    from tendenci.apps.jobs.models import JobPricing
    job_pricings = JobPricing.objects.filter(status=True).order_by('duration')
    show_premium_price = False
    show_member_price = False
    premium_jp = JobPricing.objects.filter(status=True).filter(premium_price__gt=0)
    if premium_jp:
        show_premium_price = True
    member_jp = JobPricing.objects.filter(status=True).filter(show_member_pricing=True).filter(Q(premium_price_member__gt=0) | Q(regular_price_member__gt=0))
    if member_jp:
        show_member_price = True
    context.update({
        "job_pricings": job_pricings,
        'show_premium_price': show_premium_price,
        'show_member_price': show_member_price
    })
    return context


@register.inclusion_tag("jobs/top_nav_items_pricing.html", takes_context=True)
def job_pricing_current_app(context, user, job_pricing=None):
    context.update({
        'app_object': job_pricing,
        "user": user
    })
    return context


class ListJobCategoriesNode(ListNode):
    model = Job
    perms = 'jobs.view_job'
    
    def render(self, context):
        user = AnonymousUser()

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                user = self.kwargs['user']
        else:
            # check the context for an already existing user
            if 'user' in context:
                user = context['user']

        filters = get_query_filters(user, self.perms)
        items = self.model.objects.filter(filters).exclude(cat=None
                                ).values('cat__name', 'cat__id'
                                ).annotate(total=Count('cat')).order_by('cat__name')

        context[self.context_var] = items

        return ""


@register.tag
def list_jobs_categories(parser, token):
    """
    Used to pull a list of jobs categories with the number of jobs per category.

    Usage::

        {% list_jobs_categories as [varname] [options] %}

    Options include:

        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**

    Example::

        {% list_jobs_categories as jobs_cats_list user=request.user %}
        {% if jobs_cats_list %}
        <ul>
        {% for cat in jobs_cats_list %}
            <li>
            <a href="{% url 'jobs' %}?cat={{ cat.cat__id }}">{{ cat.cat__name }} ({{ cat.total }})</a>
            </li>
        {% endfor %}
        </ul>
        {% endif %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    return ListJobCategoriesNode(context_var, *args, **kwargs)


class ListJobNode(ListNode):
    model = Job
    perms = 'jobs.view_job'


@register.tag
def list_jobs(parser, token):
    """
    Used to pull a list of :model:`jobs.Job` items.

    Usage::

        {% list_jobs as [varname] [options] %}

    Be sure the [varname] has a specific name like ``jobs_sidebar`` or
    ``jobs_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Approved**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_jobs as jobs_list limit=5 tags="cool" %}
        {% for job in jobs_list %}
            {{ job.title }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-post_dt'

    return ListJobNode(context_var, *args, **kwargs)
