import random
from operator import or_

from django.template import Node, Variable, Context, loader
from django.db import models
from django.core.exceptions import FieldError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q

from tendenci.apps.user_groups.models import Group
from tendenci.apps.perms.utils import get_query_filters


def parse_tag_kwargs(bits):
    """
    Takes in template tag bits and parses out the kwargs

    from tendenci.apps.base.template_tags import parse_tag_kwargs

    bits = token.split_contents()
    kwargs = parse_tag_kwargs(bits)
    """
    kwargs = {}

    for bit in bits:
        if '=' in bit:
            key = bit.split("=", 1)[0]
            value = bit.split("=", 1)[1]
            kwargs[key] = value

    return kwargs


class ListNode(Node):
    """
    Base template node for searching for items in haystack

    Searches haystack based on template tag arg and kwargs
    and will return a SearchQuerySet

    from tendenci.apps.base.template_tags import ListNode

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
        if 'query' in self.kwargs and not hasattr(self.model.objects, 'search'):
            raise AttributeError(_('Model.objects does not have a search method'))

    def custom_model_filter(self, items, user):
        """Returns a queryset that may have custom filtering.

        This is useful for models that filter on a datefield to prevent
        items published in the future from displaying.

        The user object is also included if permissions are relevant to
        the filtering.
        """
        return items

    def render(self, context):
        tags = u''
        query = u''
        user = AnonymousUser()
        limit = 3
        order = u''
        exclude = u''
        randomize = False
        group = u''
        status_detail = u'active'

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
        # for performance reason, if user is not passed in, use AnonymousUser
#         else:
#             # check the context for an already existing user
#             # and see if it is really a user object
#             if 'user' in context:
#                 if isinstance(context['user'], User):
#                     user = context['user']

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
                exclude = unicode(exclude.resolve(context))
            except:
                exclude = self.kwargs['exclude']

            exclude = exclude.replace('"', '')
            exclude = exclude.split(',')

        if 'group' in self.kwargs:
            try:
                group = Variable(self.kwargs['group'])
                group = unicode(group.resolve(context))
            except:
                group = self.kwargs['group']

            try:
                group = int(group)
            except:
                group = None

        if 'status_detail' in self.kwargs:
            try:
                status_detail = Variable(self.kwargs['status_detail'])
                status_detail = status_detail.resolve(context)
            except:
                status_detail = self.kwargs['status_detail']

        # get the list of items
        self.perms = getattr(self, 'perms', unicode())

        # Only use the search index if there is a query passed
        if query:
            for tag in tags:
                tag = tag.strip()
                query = '%s "tag:%s"' % (query, tag)

            items = self.model.objects.search(user=user, query=query)

        else:
            filters = get_query_filters(user, self.perms)
            items = self.model.objects.filter(filters)
            if user.is_authenticated():
                items = items.distinct()

            if tags:  # tags is a comma delimited list
                # this is fast; but has one hole
                # it finds words inside of other words
                # e.g. "prev" is within "prevent"
                tag_queries = [Q(tags__iexact=t.strip()) for t in tags]
                tag_queries += [Q(tags__istartswith=t.strip() + ",") for t in tags]
                tag_queries += [Q(tags__iendswith=", " + t.strip()) for t in tags]
                tag_queries += [Q(tags__iendswith="," + t.strip()) for t in tags]
                tag_queries += [Q(tags__icontains=", " + t.strip() + ",") for t in tags]
                tag_queries += [Q(tags__icontains="," + t.strip() + ",") for t in tags]
                tag_query = reduce(or_, tag_queries)
                items = items.filter(tag_query)

            if hasattr(self.model, 'group') and group:
                items = items.filter(group=group)
            if hasattr(self.model, 'groups') and group:
                items = items.filter(groups__in=[group])

            if hasattr(self.model(), 'status_detail'):
                items = items.filter(status_detail__iexact=status_detail)

            items = self.custom_model_filter(items, user)

        objects = []

        # exclude certain primary keys
        if exclude:
            excludes = []
            for ex in exclude:
                if ex.isdigit():
                    excludes.append(int(ex))
            if query:
                items = items.exclude(primary_key__in=excludes)
            else:
                items = items.exclude(pk__in=excludes)

        # if order is not specified it sorts by relevance
        if order:
            items = items.order_by(order)

        if randomize:
            objects = [item for item in random.sample(items, len(items))][:limit]
        else:
            objects = [item for item in items[:limit]]

        if query:
            objects = [item.object for item in objects]

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
