from tagging.models import Tag, TaggedItem

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.db.models import Count

from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.event_logs.models import EventLog

@login_required
def tags_list(request, template_name="tags/list.html"):
    tags = Tag.objects.all().annotate(num=Count('items')).order_by('-num')
    content_types = []
    content_type_tags = ContentType.objects.all().annotate(ct_count=Count('taggeditem')).order_by('name')
    for ct in content_type_tags:
        if ct.ct_count > 0:
            item = {}
            item['name'] = ct.name
            item['tags'] = Tag.objects.filter(items__content_type=ct).annotate(num=Count('items')).order_by('-num')
            content_types.append(item)

    EventLog.objects.log()
    return render_to_response(template_name, {'tags': tags, 'content_types': content_types},
        context_instance=RequestContext(request))


@login_required
def detail(request, id=None, template_name="tags/detail.html"):
    tag = get_object_or_404(Tag, pk=id)
    tagged_items = TaggedItem.objects.filter(tag=tag).order_by('content_type__name', 'tag__name')

    EventLog.objects.log(instance=tag)
    return render_to_response(template_name, {'tag': tag, 'tagged_items': tagged_items},
        context_instance=RequestContext(request))