from django.urls import path, re_path
from tendenci.apps.campaign_monitor.signals import init_signals
from . import views

init_signals()

urlpatterns = [
    re_path(r'^$', views.template_index),
    re_path(r'^templates/$', views.template_index, name="campaign_monitor.template_index"),
    re_path(r'^templates/add/$', views.template_add, name="campaign_monitor.template_add"),
    re_path(r'^templates/sync/$', views.template_sync, name="campaign_monitor.template_sync"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/page.html$', views.template_html, name="campaign_monitor.template_html"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/original.html$', views.template_html_original, name="campaign_monitor.template_html_original"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/render/$', views.template_render, name="campaign_monitor.template_render"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/text/$', views.template_text, name="campaign_monitor.template_text"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/edit/$', views.template_edit, name="campaign_monitor.template_edit"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/delete/$', views.template_delete, name="campaign_monitor.template_delete"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/update/$', views.template_update, name="campaign_monitor.template_update"),
    re_path(r'^templates/(?P<template_id>[\w\-\/]+)/$', views.template_view, name="campaign_monitor.template_view"),
    re_path(r'^campaigns/$', views.campaign_index, name="campaign_monitor.campaign_index"),
    re_path(r'^campaigns/sync/$', views.campaign_sync, name="campaign_monitor.campaign_sync"),
    re_path(r'^campaigns/generate/$', views.campaign_generate, name="campaign_monitor.campaign_generate"),
    re_path(r'^campaigns/delete/(?P<campaign_id>[\w\-\/]+)/$', views.campaign_delete, name="campaign_monitor.campaign_delete"),
    re_path(r'^campaigns/(?P<campaign_id>[\w\-\/]+)/$', views.campaign_view, name="campaign_monitor.campaign_view"),
]
