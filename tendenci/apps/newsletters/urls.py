from django.conf.urls.defaults import patterns, url

from tendenci.core.newsletters.views import NewsletterGeneratorView

urlpatterns = patterns('tendenci.core.newsletters.views',
    url(r'^newsletter_generator/', NewsletterGeneratorView.as_view(), name="newsletter.generator"),
    url(r'^newsletters/templates/(?P<template_id>[\w\-\/]+)/render/$', 'template_view', name="newsletter.template_render"),
    url(r'^newsletters/templates/(?P<template_id>[\w\-\/]+)/content/$', 'template_view', {'render':False}, name="newsletter.template_content"),
    url(r'^newsletters/generate/$', 'generate', name="newsletter.generate"),
)
