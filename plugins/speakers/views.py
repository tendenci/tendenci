from os.path import basename, join, abspath, dirname

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile

from base.http import Http403
from files.utils import get_image
from perms.utils import has_perm
from perms.utils import is_admin


from models import Speaker

def index(request, slug=None):
    if not slug: return HttpResponseRedirect(reverse('speaker.search'))
    speaker = get_object_or_404(Speaker, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (speaker.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    template_name="speakers/view.html"
    
    if has_perm(request.user, 'speaker.view_speaker', speaker):
        return render_to_response(template_name, {'speaker': speaker},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="speakers/search.html"):
    query = request.GET.get('q', None)
    speakers = Speaker.objects.search(query, user=request.user)
    speakers = speakers.order_by('order')

    return render_to_response(template_name, {'speakers':speakers},
        context_instance=RequestContext(request))
