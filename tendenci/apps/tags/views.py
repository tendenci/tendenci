from tagging.models import Tag, TaggedItem

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Count
import simplejson

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp


@login_required
def tags_list(request, template_name="tags/list.html"):
    tags = Tag.objects.all().annotate(num=Count('items')).order_by('-num')
    content_types = []
    content_type_tags = ContentType.objects.all().annotate(ct_count=Count('taggeditem'))
    content_type_tags = sorted(content_type_tags, key=lambda ct: ct.name)
    for ct in content_type_tags:
        if ct.ct_count > 0:
            item = {}
            item['name'] = ct.name
            item['tags'] = Tag.objects.filter(items__content_type=ct).annotate(num=Count('items')).order_by('-num')
            content_types.append(item)
    return render_to_resp(request=request, template_name=template_name,
        context={'tags': tags, 'content_types': content_types})


@login_required
def detail(request, id=None, template_name="tags/detail.html"):
    tag = get_object_or_404(Tag, pk=id)
    tagged_items = TaggedItem.objects.filter(tag=tag)
    tagged_items = sorted(tagged_items, key=lambda i: i.content_type.name)
    return render_to_resp(request=request, template_name=template_name,
        context={'tag': tag, 'tagged_items': tagged_items})


def autocomplete(request):
    q = request.GET.get('term', '')
    if request.is_ajax() and q:
        tags = Tag.objects.filter(name__istartswith=q)
        tag_list = [{'id':tag.pk, 'label':tag.name, 'value':tag.name} for tag in tags]
        return HttpResponse(simplejson.dumps(tag_list), content_type='application/json')
    raise Http404
