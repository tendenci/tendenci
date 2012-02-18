import random

from django.template import Node, Variable, Context, loader
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AnonymousUser, User

from perms.utils import get_query_filters

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
        exclude = u''
        randomize = False

        if 'random' in self.kwargs:
            randomize = bool(self.kwargs['random'])

        if 'tags' in self.kwargs:
            try:
                tags = Variable(self.kwargs['tags'])
                tags = unicode(tags.resolve(context))
            except:
                tags = self.kwargs['tags']

            tags = tags.replace('"', '')
            tags = tags.split(',')

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                user = self.kwargs['user']
                if user == "anon" or user == "anonymous":
                    user = AnonymousUser()
        else:
            # check the context for an already existing user
            # and see if it is really a user object
            if 'user' in context:
                if isinstance(context['user'], User):
                    user = context['user']

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                limit = self.kwargs['limit']
        limit = int(limit)

        if 'query' in self.kwargs:
            try:
                query = Variable(self.kwargs['query'])
                query = query.resolve(context)
            except:
                query = self.kwargs['query']  # context string

        if 'order' in self.kwargs:
            try:
                order = Variable(self.kwargs['order'])
                order = order.resolve(context)
            except:
                order = self.kwargs['order']
                
        if 'exclude' in self.kwargs:
            try:
                exclude = Variable(self.kwargs['exclude'])
                exclude = unicode(tags.resolve(context))
            except:
                exclude = self.kwargs['exclude']

            exclude = exclude.replace('"', '')
            exclude = exclude.split(',')
        
        # process tags
        for tag in tags:
            tag = tag.strip()
            query = '%s "tag:%s"' % (query, tag)

        # get the list of items
        # items = self.model.objects.search(user=user, query=query)
        try:
            print self.perms
        except:
            self.perms = 'app.view'
        filters = get_query_filters(user, self.perms)
        items = self.model.objects.filter(filters).distinct()
        objects = []
        
        if items:
            #exclude certain primary keys
            if exclude:
                items = items.exclude(pk__in=exclude)

            # if order is not specified it sorts by relevance
            if order:
                items = items.order_by(order)

            if randomize:
                objects = [item for item in random.sample(items, len(items))][:limit]
            else:
                objects = [item for item in items[:limit]]

        context[self.context_var] = objects
        
        if 'template' in self.kwargs:
            try:
                template = Variable(self.kwargs['template'])
                template = unicode(template.resolve(context))
            except:
                template = self.kwargs['template']
                
            t = loader.get_template(template)
            return t.render(Context(context, autoescape=context.autoescape))
            
        return ""
