from django.views.generic.list_detail import object_list, object_detail
from models import Post


def list(request):
    return object_list(
        request,
        queryset=Post.objects.all(),
        allow_empty=True
    )

def detail(request, object_id):
    return object_detail(
        request,
        queryset=Post.objects.all(),
        object_id=object_id
    )
