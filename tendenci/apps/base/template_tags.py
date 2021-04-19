from builtins import str
import random
from operator import or_
from functools import reduce

from django.template import Node, Variable
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.core import exceptions

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

    def clean_field_value(self, k, v):
        """
        Clean the value `v` for the field `k`.
        """
        [field] = [field for field in self.model._meta.fields if field.name==k][:1] or [None]
        if field:
            try:
                value = field.to_python(v)
                field.run_validators(value)
            except exceptions.ValidationError:
                value = None
            return value
        return None
    
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
        user_filter = u''

        if 'random' in self.kwargs:
            randomize = bool(self.kwargs['random'])

        if 'tags' in self.kwargs:
            try:
                tags = Variable(self.kwargs['tags'])
                tags = str(tags.resolve(context))
            except:
                tags = self.kwargs['tags']

            tags = tags.replace('"', '')
            tags = tags.split(',')

        if 'filters' in self.kwargs:
            try:
                user_filter = Variable(self.kwargs['filters'])
                user_filter = user_filter.resolve(context)
            except:
                user_filter = self.kwargs['filters']

            user_filter = user_filter.replace('"', '')
            user_filter = user_filter.split(',')

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
                exclude = str(exclude.resolve(context))
            except:
                exclude = self.kwargs['exclude']

            exclude = exclude.replace('"', '')
            exclude = exclude.split(',')

        if 'group' in self.kwargs:
            try:
                group = Variable(self.kwargs['group'])
                group = str(group.resolve(context))
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
        self.perms = getattr(self, 'perms', str())

        # Only use the search index if there is a query passed
        if query:
            for tag in tags:
                tag = tag.strip()
                query = '%s "tag:%s"' % (query, tag)

            items = self.model.objects.search(user=user, query=query)

        else:
            filters = get_query_filters(user, self.perms)
            items = self.model.objects.filter(filters)
            if user.is_authenticated:
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

        # this trusts the dev a lot to not break things
        if user_filter:
            for f in user_filter:
                if "|" in f:
                    f = f.split('|')
                    f_qs = [fx.split('=') for fx in f]
                    f_query = Q()

                    for fxi in f_qs:
                        k, v = fxi[0].strip(), fxi[1].strip()
                        if hasattr(self.model, k):
                            v = self.clean_field_value(k, v)
                            if v is not None:
                                f_query.add(Q(**{k: v}), Q.OR)

                    # just filter on each find
                    items = items.filter(f_query)
                    
                else:
                    if "&" in f:
                        f = f.split('&')
                        f_qs = [fx.split('=') for fx in f]
                        f_query = Q()

                        for fxi in f_qs:
                            k, v = fxi[0].strip(), fxi[1].strip()
                            if hasattr(self.model, k):
                                v = self.clean_field_value(k, v)
                                if v is not None:
                                    f_query.add(Q(**{k: v}), Q.AND)

                        # just filter on each find
                        items = items.filter(f_query)

                    else:
                        fxi = f.split('=')
                        f_query = Q(**{fxi[0].strip(): fxi[1].strip() })
                        items = items.filter(f_query)          

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
            items = list(items)
            objects = random.sample(items, min(len(items), limit))
        else:
            objects = items[:limit]

        if query:
            objects = [item.object for item in objects]

        context[self.context_var] = objects

        if 'template' in self.kwargs:
            try:
                template = Variable(self.kwargs['template'])
                template = str(template.resolve(context))
            except:
                template = self.kwargs['template']

            t = context.template.engine.get_template(template)
            return t.render(context=context, autoescape=context.autoescape)

        return ""
