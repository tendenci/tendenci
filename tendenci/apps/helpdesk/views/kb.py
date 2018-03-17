"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

views/kb.py - Public-facing knowledgebase views. The knowledgebase is a
              simple categorised question/answer system to show common
              resolutions to common problems.
"""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.helpdesk import settings as helpdesk_settings
from tendenci.apps.helpdesk.models import KBCategory, KBItem


def index(request):
    category_list = KBCategory.objects.all()
    # TODO: It'd be great to have a list of most popular items here.
    return render_to_resp(request=request, template_name='helpdesk/kb_index.html',
        context={
            'kb_categories': category_list,
            'helpdesk_settings': helpdesk_settings,
        })


def category(request, slug):
    category = get_object_or_404(KBCategory, slug__iexact=slug)
    items = category.kbitem_set.all()
    return render_to_resp(request=request, template_name='helpdesk/kb_category.html',
        context={
            'category': category,
            'items': items,
            'helpdesk_settings': helpdesk_settings,
        })


def item(request, item):
    item = get_object_or_404(KBItem, pk=item)
    return render_to_resp(request=request, template_name='helpdesk/kb_item.html',
        context={
            'item': item,
            'helpdesk_settings': helpdesk_settings,
        })


def vote(request, item):
    item = get_object_or_404(KBItem, pk=item)
    vote = request.GET.get('vote', None)
    if vote in ('up', 'down'):
        item.votes += 1
        if vote == 'up':
            item.recommendations += 1
        item.save()

    return HttpResponseRedirect(item.get_absolute_url())
