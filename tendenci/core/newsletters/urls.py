from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from tendenci.core.newsletters.views import (
    NewsletterGeneratorView,
    NewsletterGeneratorOrigView,
    MarketingActionStepOneView,
    MarketingActionStepTwoView,
    NewsletterUpdateEmailView,
    MarketingActionStepThreeView,
    MarketingActionStepFourView,
    MarketingActionStepFiveView)

urlpatterns = patterns('tendenci.core.newsletters.views',
    url(r'^newsletter_generator/', NewsletterGeneratorView.as_view(), name="newsletter.generator"),
    url(r'^newsletter_orig_generator/', login_required(NewsletterGeneratorOrigView.as_view()), name='newsletter.orig.generator'),
    url(r'^newsletters/templates/(?P<template_id>[\w\-\/]+)/render/$', 'template_view', name="newsletter.template_render"),
    url(r'^newsletters/templates/(?P<template_id>[\w\-\/]+)/content/$', 'template_view', {'render':False}, name="newsletter.template_content"),
    url(r'^newsletters/generate/$', 'generate', name="newsletter.generate"),
    url(r'^newsletters/default_templates/view/$', 'default_template_view', name="newsletter.default_template"),

    # marketing actions urls
    url(r'^newsletters/actions/step1/(?P<pk>\d+)', login_required(MarketingActionStepOneView.as_view()), name='newsletter.action.step1'),
    url(r'^newsletters/actions/step2/(?P<pk>\d+)', login_required(MarketingActionStepTwoView.as_view()), name='newsletter.action.step2'),
    url(r'^newsletters/actions/step2/update-email(?P<pk>\d+)', login_required(NewsletterUpdateEmailView.as_view()), name='newsletter.action.step2.update-email'),
    url(r'^newsletters/actions/step3/(?P<pk>\d+)', login_required(MarketingActionStepThreeView.as_view()), name='newsletter.action.step3'),
    url(r'^newsletters/actions/step4/(?P<pk>\d+)', login_required(MarketingActionStepFourView.as_view()), name='newsletter.action.step4'),
    url(r'^newsletters/actions/step5/(?P<pk>\d+)', login_required(MarketingActionStepFiveView.as_view()), name='newsletter.action.step5'),

)