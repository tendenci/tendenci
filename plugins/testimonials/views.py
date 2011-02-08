from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse

from base.http import Http403
from perms.utils import has_perm
from perms.utils import is_admin

from models import Testimonial

def index(request, pk=None, template_name="testimonials/view.html"):
    if not pk: return HttpResponseRedirect(reverse('testimonial.search'))
    testimonial = get_object_or_404(Testimonial, pk=pk)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (testimonial.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if has_perm(request.user, 'testimonials.view_testimonial', testimonial):
        return render_to_response(template_name, {'testimonial': testimonial},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="testimonials/search.html"):
    query = request.GET.get('q', None)
    testimonials = Testimonial.objects.search(query, user=request.user)
    testimonials = testimonials.order_by('-create_dt')

    return render_to_response(template_name, {'testimonials': testimonials},
        context_instance=RequestContext(request))