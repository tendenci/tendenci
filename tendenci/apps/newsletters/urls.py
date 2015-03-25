from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.newsletters.views import (
    NewsletterGeneratorView,
    NewsletterListView,
    NewsletterGeneratorOrigView,
    MarketingActionStepOneView,
    MarketingActionStepTwoView,
    NewsletterUpdateEmailView,
    MarketingActionStepThreeView,
    MarketingActionStepFourView,
    MarketingActionStepFiveView,
    NewsletterDetailView,
    NewsletterResendView,
    NewsletterDeleteView)

urlpath = get_setting('module', 'newsletters', 'url') or 'newsletters'

urlpatterns = patterns('tendenci.apps.newsletters.views',
    url(r'^%s/$' % urlpath, login_required(NewsletterListView.as_view()), name="newsletter.list"),
    url(r'^%s/newsletter_generator/$' % urlpath, NewsletterGeneratorView.as_view(), name="newsletter.generator"),
    url(r'^%s/newsletter_orig_generator/$' % urlpath, login_required(NewsletterGeneratorOrigView.as_view()), name='newsletter.orig.generator'),
    url(r'^%s/templates/(?P<template_id>[\w\-\/]+)/render/$' % urlpath , 'template_view', name="newsletter.template_render"),
    url(r'^%s/templates/(?P<template_id>[\w\-\/]+)/content/$' % urlpath, 'template_view', {'render':False}, name="newsletter.template_content"),
    url(r'^%s/generate/$' % urlpath, 'generate', name="newsletter.generate"),
    url(r'^%s/default_templates/view/$' % urlpath, 'default_template_view', name="newsletter.default_template"),
    url(r'^%s/view/(?P<pk>\d+)/$' % urlpath, 'view_email_from_browser', name='newsletter.view_from_browser'),

    # marketing actions urls
    url(r'^%s/actions/step1/(?P<pk>\d+)/$' % urlpath, login_required(MarketingActionStepOneView.as_view()), name='newsletter.action.step1'),
    url(r'^%s/actions/step2/(?P<pk>\d+)/$' %urlpath, login_required(MarketingActionStepTwoView.as_view()), name='newsletter.action.step2'),
    url(r'^%s/actions/step2/update-email/(?P<pk>\d+)/$' % urlpath, login_required(NewsletterUpdateEmailView.as_view()), name='newsletter.action.step2.update-email'),
    url(r'^%s/actions/step3/(?P<pk>\d+)/$' % urlpath, login_required(MarketingActionStepThreeView.as_view()), name='newsletter.action.step3'),
    url(r'^%s/actions/step4/(?P<pk>\d+)/$' % urlpath, login_required(MarketingActionStepFourView.as_view()), name='newsletter.action.step4'),
    url(r'^%s/actions/step5/(?P<pk>\d+)/$' % urlpath, login_required(MarketingActionStepFiveView.as_view()), name='newsletter.action.step5'),

    url(r'^%s/view/details/(?P<pk>\d+)/$' % urlpath, login_required(NewsletterDetailView.as_view()), name='newsletter.detail.view'),
    url(r'^%s/resend/(?P<pk>\d+)/$' % urlpath, login_required(NewsletterResendView.as_view()), name='newsletter.resend.view'),
    url(r'^%s/delete/(?P<pk>\d+)/$' % urlpath, login_required(NewsletterDeleteView.as_view()), name='newsletter.delete'),

)
