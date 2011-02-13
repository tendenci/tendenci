import random

from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from staff.models import Staff

register = Library()

@register.inclusion_tag("staff/options.html", takes_context=True)
def staff_options(context, user, staff):
    context.update({
        "opt_object": staff,
        "user": user
    })
    return context

@register.inclusion_tag("staff/search-form.html", takes_context=True)
def staff_search(context):
    return context


class ListStaffNode(Node):
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

        # get the list of staff
        staff_members = Staff.objects.search(user=user, query=query)
        staff_members = staff_members.order_by(order)
        if randomize:
            staff_members = [member.object for member in random.sample(staff_members, staff_members.count())][:limit]
        else:
            staff_members = [member.object for member in staff_members[:limit]]

        context[self.context_var] = staff_members
        return ""

@register.tag
def list_staff(parser, token):
    """
    Example:
        {% list_staff as the_staff user=user limit=3 %}
        {% for staff_member in the_staff %}
            {{ staff_member.name }}
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

    return ListStaffNode(context_var, *args, **kwargs)