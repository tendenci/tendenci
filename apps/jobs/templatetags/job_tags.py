import random

from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from jobs.models import Job

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
    from jobs.models import JobPricing
    job_pricings = JobPricing.objects.filter(status=1).order_by('duration')
    show_premium_price = False
    show_member_price = False
    premium_jp = JobPricing.objects.filter(status=1).filter(premium_price__gt=0)
    if premium_jp:
        show_premium_price = True
    member_jp = JobPricing.objects.filter(status=1).filter(regular_price_member__gt=0)
    if member_jp:
        show_member_price = True
    context.update({
        "job_pricings": job_pricings,
        'show_premium_price': show_premium_price,
        'show_member_price': show_member_price
    })
    return context
    
class ListJobNode(Node):
    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        tags = u''
        query = u''
        user = AnonymousUser()
        limit = 3
        order = u'-create_dt'
        randomize = False
        
        if 'random' in self.kwargs:
            randomize = True

        if 'tags' in self.kwargs:
            try:
                tags = Variable(self.kwargs['tags'])
                tags = unicode(tags.resolve(context))
            except:
                tags = self.kwargs['tags'] # context string
            tags = tags.split(',')

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                pass # use user default
        else:
            # check the context for an already existing user
            if 'user' in context:
                user = context['user']

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                pass # use limit default

        if 'query' in self.kwargs:
            try:
                query = Variable(self.kwargs['query'])
                query = query.resolve(context)
            except:
                query = self.kwargs['query'] # context string

        if 'order' in self.kwargs:
            try:
                order = Variable(self.kwargs['order'])
                order = order.resolve(context)
            except:
                pass # use order default
        
        # process tags
        for tag in tags:
            tag = tag.strip()
            query = '%s "tag:%s"' % (query, tag)

        # get the list of jobs
        jobs = Job.objects.search(user=user, query=query)
        jobs = jobs.order_by(order)
        if randomize:
            jobs = [job.object for job in random.sample(jobs, jobs.count())][:limit]
        else:
            jobs = [job.object for job in jobs[:limit]]

        context[self.context_var] = jobs
        return ""

@register.tag
def list_jobs(parser, token):
    """
    Example:
        {% list_jobs as jobs_list [user=user limit=3 order"title" q="engineering"] %}
        {% for job in jobs_list %}
            {{ job.title }}
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

    for bit in bits:
        if "limit=" in bit:
            kwargs["limit"] = bit.split("=")[1]
        if "user=" in bit:
            kwargs["user"] = bit.split("=")[1]
        if "tags=" in bit:
            kwargs["tags"] = bit.split("=")[1].replace('"','')
        if "q=" in bit:
            kwargs["query"] = bit.split("=")[1]
        if "order=" in bit:
            kwargs["order"] = bit.split("=")[1]
        if "random" in bit:
            kwargs["random"] = True

    return ListJobNode(context_var, *args, **kwargs)