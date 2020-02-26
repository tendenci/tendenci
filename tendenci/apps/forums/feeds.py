# -*- coding: utf-8 -*-


from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from .models import Post, Topic

from .permissions import perms

class PybbFeed(Feed):
    feed_type = Atom1Feed

    def __init__(self):
        super(PybbFeed, self).__init__()
        self.__qualname__ = self.__class__.__name__  # https://code.djangoproject.com/ticket/29296

    def link(self):
        return reverse('pybb:index')

    def item_guid(self, obj):
        return str(obj.id)

    def item_pubdate(self, obj):
        return obj.created


class LastPosts(PybbFeed):
    title = _('Latest posts on forum')
    description = _('Latest posts on forum')
    title_template = 'pybb/feeds/posts_title.html'
    description_template = 'pybb/feeds/posts_description.html'

    def get_object(self, request, *args, **kwargs):
        return request.user

    def items(self, user):
        ids = [p.id for p in perms.filter_posts(user, Post.objects.only('id')).order_by('-created', '-id')[:15]]
        return Post.objects.filter(id__in=ids).select_related('topic', 'topic__forum', 'user')


class LastTopics(PybbFeed):
    title = _('Latest topics on forum')
    description = _('Latest topics on forum')
    title_template = 'pybb/feeds/topics_title.html'
    description_template = 'pybb/feeds/topics_description.html'

    def get_object(self, request, *args, **kwargs):
        return request.user

    def items(self, user):
        return perms.filter_topics(user, Topic.objects.all()).select_related('forum').order_by('-created', '-id')[:15]
