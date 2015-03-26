from django.conf.urls import patterns, url
from tendenci.apps.campaign_monitor.signals import init_signals


init_signals()


urlpatterns = patterns('tendenci.apps.campaign_monitor.views',
    url(r'^$', 'template_index'),
    url(r'^templates/$', 'template_index', name="campaign_monitor.template_index"),
    url(r'^templates/add/$', 'template_add', name="campaign_monitor.template_add"),
    url(r'^templates/sync/$', 'template_sync', name="campaign_monitor.template_sync"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/page.html$', 'template_html', name="campaign_monitor.template_html"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/original.html$', 'template_html_original', name="campaign_monitor.template_html_original"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/render/$', 'template_render', name="campaign_monitor.template_render"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/text/$', 'template_text', name="campaign_monitor.template_text"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/edit/$', 'template_edit', name="campaign_monitor.template_edit"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/delete/$', 'template_delete', name="campaign_monitor.template_delete"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/update/$', 'template_update', name="campaign_monitor.template_update"),
    url(r'^templates/(?P<template_id>[\w\-\/]+)/$', 'template_view', name="campaign_monitor.template_view"),
    url(r'^campaigns/$', 'campaign_index', name="campaign_monitor.campaign_index"),
    url(r'^campaigns/sync/$', 'campaign_sync', name="campaign_monitor.campaign_sync"),
    url(r'^campaigns/generate/$', 'campaign_generate', name="campaign_monitor.campaign_generate"),
    url(r'^campaigns/delete/(?P<campaign_id>[\w\-\/]+)/$', 'campaign_delete', name="campaign_monitor.campaign_delete"),
    url(r'^campaigns/(?P<campaign_id>[\w\-\/]+)/$', 'campaign_view', name="campaign_monitor.campaign_view"),

)
