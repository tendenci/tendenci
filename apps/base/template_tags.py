import random

from django.template import Node, Variable
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AnonymousUser


def parse_tag_kwargs(bits):
    """
    Takes in template tag bits and parses out the kwargs

    from base.template_tags import parse_tag_kwargs

    bits = token.split_contents()
    kwargs = parse_tag_kwargs(bits)
    """
    kwargs = {}

    for bit in bits:
        if '=' in bit:
            key, value = bit.split('=')
            kwargs[key] = value

    return kwargs


class ListNode(Node):
    """
    Base template node for searching for items in haystack

    Searches haystack based on template tag arg and kwargs
    and will return a SearchQuerySet

    from base.template_tags import ListNode

    class MyModelListNode(ListNode):
        model = MyModel
    """
    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

        if not self.model:
            raise AttributeError(_('Model attribute must be set'))
        if not issubclass(self.model, models.Model):
            raise AttributeError(_('Model attribute must derive from Model'))
        if not hasattr(self.model.objects, 'search'):
            raise AttributeError(_('Model.objects does not have a search method'))

    def render(self, context):
        tags = u''
        query = u''
        user = AnonymousUser()
        limit = 3
        order = u''
        randomize = False

        if 'random' in self.kwargs:
            randomize = bool(self.kwargs['random'])

        if 'tags' in self.kwargs:
            if self.kwargs['tags'] == 'tags':
                try:
                    tags = Variable(self.kwargs['tags'])
                    tags = unicode(tags.resolve(context))
                except:
                    tags = self.kwargs['tags']
            else:
                tags = self.kwargs['tags']
            tags = tags.replace('"', '')
            tags = tags.split(',')

        if 'user' in self.kwargs:
            if self.kwargs['user'] == 'user':
                try:
                    user = Variable(self.kwargs['user'])
                    user = user.resolve(context)
                except:
                    pass
            else:
                user = self.kwargs['user']
        else:
            # check the context for an already existing user
            if 'user' in context:
                user = context['user']

        if 'limit' in self.kwargs:
            if self.kwargs['limit'] == 'limit':
                try:
                    limit = Variable(self.kwargs['limit'])
                    limit = limit.resolve(context)
                except:
                    pass
            else:
                limit = self.kwargs['limit']

        if 'query' in self.kwargs:
            if self.kwargs['query'] == 'query':
                try:
                    query = Variable(self.kwargs['query'])
                    query = query.resolve(context)
                except:
                    query = self.kwargs['query']  # context string
            else:
                query = self.kwargs['query']

        if 'order' in self.kwargs:
            if self.kwargs['order'] == 'order':
                try:
                    order = Variable(self.kwargs['order'])
                    order = order.resolve(context)
                except:
                    pass
            else:
                order = self.kwargs['order']

        # process tags
        for tag in tags:
            tag = tag.strip()
            query = '%s "tag:%s"' % (query, tag)

        # get the list of staff
        items = self.model.objects.search(user=user, query=query)

        # if order is not specified it sorts by relevance
        if order:
            items = items.order_by(order)

        if randomize:
            objects = [item.object for item in random.sample(items, items.count())][:limit]
        else:
            objects = [item.object for item in items[:limit]]

        context[self.context_var] = objects
        return ""
