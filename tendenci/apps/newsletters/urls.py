from django.conf.urls import url
from tendenci.apps.site_settings.utils import get_setting
from django.contrib.auth.decorators import login_required
from . import views

urlpath = get_setting('module', 'newsletters', 'url') or 'newsletters'

urlpatterns = [
    url(r'^%s/$' % urlpath, login_required(views.NewsletterListView.as_view()), name="newsletter.list"),
    url(r'^%s/newsletter_generator/$' % urlpath, views.NewsletterGeneratorView.as_view(), name="newsletter.generator"),
    url(r'^%s/newsletter_orig_generator/$' % urlpath, login_required(views.NewsletterGeneratorOrigView.as_view()), name='newsletter.orig.generator'),
    url(r'^%s/templates/(?P<template_id>[\w\-\/]+)/render/$' % urlpath , views.template_view, name="newsletter.template_render"),
    url(r'^%s/templates/(?P<template_id>[\w\-\/]+)/content/$' % urlpath, views.template_view, {'render':False}, name="newsletter.template_content"),
    url(r'^%s/generate/$' % urlpath, views.generate, name="newsletter.generate"),
    url(r'^%s/default_templates/view/$' % urlpath, views.default_template_view, name="newsletter.default_template"),
    url(r'^%s/view/(?P<pk>\d+)/$' % urlpath, views.view_email_from_browser, name='newsletter.view_from_browser'),

    # marketing actions urls
    url(r'^%s/actions/step1/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepOneView.as_view()), name='newsletter.action.step1'),
    url(r'^%s/actions/step2/(?P<pk>\d+)/$' %urlpath, login_required(views.MarketingActionStepTwoView.as_view()), name='newsletter.action.step2'),
    url(r'^%s/actions/step2/update-email/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterUpdateEmailView.as_view()), name='newsletter.action.step2.update-email'),
    url(r'^%s/actions/step3/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepThreeView.as_view()), name='newsletter.action.step3'),
    url(r'^%s/actions/step4/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepFourView.as_view()), name='newsletter.action.step4'),
    url(r'^%s/actions/step5/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepFiveView.as_view()), name='newsletter.action.step5'),

    url(r'^%s/view/details/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterDetailView.as_view()), name='newsletter.detail.view'),
    url(r'^%s/clone/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterCloneView.as_view()), name='newsletter.clone'),
    url(r'^%s/resend/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterResendView.as_view()), name='newsletter.resend.view'),
    url(r'^%s/delete/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterDeleteView.as_view()), name='newsletter.delete'),
]
