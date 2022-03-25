# -*- coding: utf-8 -*-

from django.urls import path, re_path
from .feeds import LastPosts, LastTopics
from . import views
from .defaults import PYBB_NICE_URL

app_name = 'pybb'

urlpatterns = [
                       # Syndication feeds
                       re_path(r'^feeds/posts/$', LastPosts(), name='feed_posts'),
                       re_path(r'^feeds/topics/$', LastTopics(), name='feed_topics'),
                       ]

urlpatterns += [
                        # Index, Category, Forum
                        re_path(r'^$', views.IndexView.as_view(), name='index'),
                        re_path(r'^category/(?P<pk>\d+)/$', views.CategoryView.as_view(), name='category'),
                        re_path(r'^forum/(?P<pk>\d+)/$', views.ForumView.as_view(), name='forum'),

                        # User
                        re_path(r'^users/(?P<username>[^/]+)/$', views.UserView.as_view(), name='user'),
                        re_path(r'^block_user/([^/]+)/$', views.block_user, name='block_user'),
                        re_path(r'^unblock_user/([^/]+)/$', views.unblock_user, name='unblock_user'),
                        re_path(r'^users/(?P<username>[^/]+)/topics/$', views.UserTopics.as_view(), name='user_topics'),
                        re_path(r'^users/(?P<username>[^/]+)/posts/$', views.UserPosts.as_view(), name='user_posts'),

                        # Profile
                        re_path(r'^profile/edit/$', views.ProfileEditView.as_view(), name='edit_profile'),

                        # Topic
                        re_path(r'^topic/(?P<pk>\d+)/$', views.TopicView.as_view(), name='topic'),
                        re_path(r'^topic/(?P<pk>\d+)/stick/$', views.StickTopicView.as_view(), name='stick_topic'),
                        re_path(r'^topic/(?P<pk>\d+)/unstick/$', views.UnstickTopicView.as_view(), name='unstick_topic'),
                        re_path(r'^topic/(?P<pk>\d+)/close/$', views.CloseTopicView.as_view(), name='close_topic'),
                        re_path(r'^topic/(?P<pk>\d+)/open/$', views.OpenTopicView.as_view(), name='open_topic'),
                        re_path(r'^topic/(?P<pk>\d+)/poll_vote/$', views.TopicPollVoteView.as_view(), name='topic_poll_vote'),
                        re_path(r'^topic/(?P<pk>\d+)/cancel_poll_vote/$', views.topic_cancel_poll_vote, name='topic_cancel_poll_vote'),
                        re_path(r'^topic/latest/$', views.LatestTopicsView.as_view(), name='topic_latest'),

                        # Add topic/post
                        re_path(r'^forum/(?P<forum_id>\d+)/topic/add/$', views.AddPostView.as_view(), name='add_topic'),
                        re_path(r'^topic/(?P<topic_id>\d+)/post/add/$', views.AddPostView.as_view(), name='add_post'),

                        # Post
                        re_path(r'^post/(?P<pk>\d+)/$', views.PostView.as_view(), name='post'),
                        re_path(r'^post/(?P<pk>\d+)/edit/$', views.EditPostView.as_view(), name='edit_post'),
                        re_path(r'^post/(?P<pk>\d+)/delete/$', views.DeletePostView.as_view(), name='delete_post'),
                        re_path(r'^post/(?P<pk>\d+)/moderate/$', views.ModeratePost.as_view(), name='moderate_post'),

                        # Attachment
                        #re_path(r'^attachment/(\w+)/$', views.show_attachment, name='pybb_attachment'),

                        # Subscription
                        re_path(r'^subscription/topic/(\d+)/delete/$',
                            views.delete_subscription, name='delete_subscription'),
                        re_path(r'^subscription/topic/(\d+)/add/$',
                            views.add_subscription, name='add_subscription'),

                        # API
                        re_path(r'^api/post_ajax_preview/$', views.post_ajax_preview, name='post_ajax_preview'),

                        # Commands
                        re_path(r'^mark_all_as_read/$', views.mark_all_as_read, name='mark_all_as_read')
                        ]

if PYBB_NICE_URL:
    urlpatterns += [
                            re_path(r'^c/(?P<slug>[\w-]+)/$', views.CategoryView.as_view(), name='category'),
                            re_path(r'^c/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$', views.ForumView.as_view(),
                                name='forum'),
                            re_path(r'^c/(?P<category_slug>[\w-]+)/(?P<forum_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
                                views.TopicView.as_view(), name='topic'),
                            ]
