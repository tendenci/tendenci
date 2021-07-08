from django.urls import path, re_path
from tendenci.apps.site_settings.utils import get_setting
from django.contrib.auth.decorators import login_required
from . import views

urlpath = get_setting('module', 'newsletters', 'url') or 'newsletters'

urlpatterns = [
    re_path(r'^%s/$' % urlpath, login_required(views.NewsletterListView.as_view()), name="newsletter.list"),
    re_path(r'^%s/newsletter_generator/$' % urlpath, views.NewsletterGeneratorView.as_view(), name="newsletter.generator"),
    re_path(r'^%s/newsletter_orig_generator/$' % urlpath, login_required(views.NewsletterGeneratorOrigView.as_view()), name='newsletter.orig.generator'),
    re_path(r'^%s/templates/(?P<template_id>[\w\-\/]+)/render/$' % urlpath , views.template_view, name="newsletter.template_render"),
    re_path(r'^%s/templates/(?P<template_id>[\w\-\/]+)/content/$' % urlpath, views.template_view, {'render':False}, name="newsletter.template_content"),
    re_path(r'^%s/generate/$' % urlpath, views.generate, name="newsletter.generate"),
    re_path(r'^%s/default_templates/view/$' % urlpath, views.default_template_view, name="newsletter.default_template"),
    re_path(r'^%s/view/(?P<pk>\d+)/$' % urlpath, views.view_email_from_browser, name='newsletter.view_from_browser'),

    # marketing actions urls
    re_path(r'^%s/actions/step1/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepOneView.as_view()), name='newsletter.action.step1'),
    re_path(r'^%s/actions/step2/(?P<pk>\d+)/$' %urlpath, login_required(views.MarketingActionStepTwoView.as_view()), name='newsletter.action.step2'),
    re_path(r'^%s/actions/step2/update-email/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterUpdateEmailView.as_view()), name='newsletter.action.step2.update-email'),
    re_path(r'^%s/actions/step3/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepThreeView.as_view()), name='newsletter.action.step3'),
    re_path(r'^%s/actions/step4/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepFourView.as_view()), name='newsletter.action.step4'),
    re_path(r'^%s/actions/step5/(?P<pk>\d+)/$' % urlpath, login_required(views.MarketingActionStepFiveView.as_view()), name='newsletter.action.step5'),

    re_path(r'^%s/view/details/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterDetailView.as_view()), name='newsletter.detail.view'),
    re_path(r'^%s/clone/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterCloneView.as_view()), name='newsletter.clone'),
    re_path(r'^%s/resend/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterResendView.as_view()), name='newsletter.resend.view'),
    re_path(r'^%s/delete/(?P<pk>\d+)/$' % urlpath, login_required(views.NewsletterDeleteView.as_view()), name='newsletter.delete'),
]
