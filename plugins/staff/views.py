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


from models import Staff

def index(request, slug=None, cv=None):
    if not slug: return HttpResponseRedirect(reverse('staff.search'))
    staff = get_object_or_404(Staff, slug=slug)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (staff.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if cv:
        template_name="staff/cv.html"
    else:
        template_name="staff/view.html"
    
    if has_perm(request.user, 'staff.view_staff', staff):
        return render_to_response(template_name, {'staff': staff},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="staff/search.html"):
    query = request.GET.get('q', None)
    staff = Staff.objects.search(query, user=request.user)
    staff = staff.order_by('start_date')

    return render_to_response(template_name, {'staff':staff},
        context_instance=RequestContext(request))
        
def photo(request, pk, size):
    if not id: raise Http404
    staff = get_object_or_404(Staff, pk=pk)

    image = None
    default_image = join(abspath(dirname(__file__)),'media','default.jpg')
    
    # get the default size
    size = tuple([int(size) for size in size.split('x')])
    if size < (24, 24):
        size = (24, 24)

    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (staff.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http404

    # get image binary
    image =  staff.photo
    if not staff.photo:
        image = ImageFile(open(default_image,'rb'))

    # set up the response
    response = HttpResponse(mimetype='image/jpeg')
    response['Content-Disposition'] = 'filename=%s'% (basename(image.name))

    # save the image to the response
    image = get_image(image, size, constrain=True, cache=True)
    image.save(response, "JPEG", quality=100)

    # output the image
    return response