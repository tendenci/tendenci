from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('newsletters.views', 
    url(r'^add/$', 'add', name="newsletter.add"),                 
    #url(r'^templates/default/(?P<template_name>[-_.\w\s]+)$', 'view_template',
    #    {'template_path': 'newsletters/templates/default/'}, 
    #    name="newsletter.view_default_template"),
    url(r'^templates/(?P<template_name>[-_./\w\s]+)$', 'view_template', 
        name="newsletter.view_template"),
    
)