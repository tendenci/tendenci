# -*- coding: utf-8 -*-

from django.conf.urls import url
from .feeds import LastPosts, LastTopics
from . import views
from .defaults import PYBB_NICE_URL

app_name = 'pybb'

urlpatterns = [
                       # Syndication feeds
                       url(r'^feeds/posts/$', LastPosts(), name='feed_posts'),
                       url(r'^feeds/topics/$', LastTopics(), name='feed_topics'),
                       ]

urlpatterns += [
                        # Index, Category, Forum
                        url(r'^$', views.IndexView.as_view(), name='index'),
                        url(r'^category/(?P<pk>\d+)/$', views.CategoryView.as_view(), name='category'),
                        url(r'^forum/(?P<pk>\d+)/$', views.ForumView.as_view(), name='forum'),

                        # User
                        url(r'^users/(?P<username>[^/]+)/$', views.UserView.as_view(), name='user'),
                        url(r'^block_user/([^/]+)/$', views.block_user, name='block_user'),
                        url(r'^unblock_user/([^/]+)/$', views.unblock_user, name='unblock_user'),
                        url(r'^users/(?P<username>[^/]+)/topics/$', views.UserTopics.as_view(), name='user_topics'),
                        url(r'^users/(?P<username>[^/]+)/posts/$', views.UserPosts.as_view(), name='user_posts'),

                        # Profile
                        url(r'^profile/edit/$', views.ProfileEditView.as_view(), name='edit_profile'),

                        # Topic
                        url(r'^topic/(?P<pk>\d+)/$', views.TopicView.as_view(), name='topic'),
                        url(r'^topic/(?P<pk>\d+)/stick/$', views.StickTopicView.as_view(), name='stick_topic'),
                        url(r'^topic/(?P<pk>\d+)/unstick/$', views.UnstickTopicView.as_view(), name='unstick_topic'),
                        url(r'^topic/(?P<pk>\d+)/close/$', views.CloseTopicView.as_view(), name='close_topic'),
                        url(r'^topic/(?P<pk>\d+)/open/$', views.OpenTopicView.as_view(), name='open_topic'),
                        url(r'^topic/(?P<pk>\d+)/poll_vote/$', views.TopicPollVoteView.as_view(), name='topic_poll_vote'),
                        url(r'^topic/(?P<pk>\d+)/cancel_poll_vote/$', views.topic_cancel_poll_vote, name='topic_cancel_poll_vote'),
                        url(r'^topic/latest/$', views.LatestTopicsView.as_view(), name='topic_latest'),

                        # Add topic/post
                        url(r'^forum/(?P<forum_id>\d+)/topic/add/$', views.AddPostView.as_view(), name='add_topic'),
                        url(r'^topic/(?P<topic_id>\d+)/post/add/$', views.AddPostView.as_view(), name='add_post'),

                        # Post
                        url(r'^post/(?P<pk>\d+)/$', views.PostView.as_view(), name='post'),
                        url(r'^post/(?P<pk>\d+)/edit/$', views.EditPostView.as_view(), name='edit_post'),
                        url(r'^post/(?P<pk>\d+)/delete/$', views.DeletePostView.as_view(), name='delete_post'),
                        url(r'^post/(?P<pk>\d+)/moderate/$', views.ModeratePost.as_view(), name='moderate_post'),

                        # Attachment
                        #url(r'^attachment/(\w+)/$', views.show_attachment, name='pybb_attachment'),

                        # Subscription
                        url(r'^subscription/topic/(\d+)/delete/$',
                            views.delete_subscription, name='delete_subscription'),
                        url(r'^subscription/topic/(\d+)/add/$',
                            views.add_subscription, name='add_subscription'),

                        # API
                        url(r'^api/post_ajax_preview/$', views.post_ajax_preview, name='post_ajax_preview'),

                        # Commands
                        url(r'^mark_all_as_read/$', views.mark_all_as_read, name='mark_all_as_read')
                        ]

if PYBB_NICE_URL:
    urlpatterns += [
                            url(r'^c/(?P<slug>[\w-]+)/$', views.CategoryView.as_view(), name='category'),
                            url(r'^c/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$', views.ForumView.as_view(),
                                name='forum'),
                            url(r'^c/(?P<category_slug>[\w-]+)/(?P<forum_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
                                views.TopicView.as_view(), name='topic'),
                            ]
