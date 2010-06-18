from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from contributions.models import Contribution

@login_required
def index(request, id=None, template_name="contributions/view.html"):
    if not id: return HttpResponseRedirect(reverse('contribution.search'))
    contribution = get_object_or_404(Contribution, pk=id)
    
    if request.user.has_perm('contributions.view_contribution', contribution):
        return render_to_response(template_name, {'contribution': contribution}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def search(request, template_name="contributions/search.html"):
    query = request.GET.get('q', None)
    contributions = Contribution.objects.search(query, user=request.user)

    
    
    return render_to_response(template_name, {'contributions':contributions}, 
        context_instance=RequestContext(request))

@login_required
def print_view(request, id, template_name="contributions/print-view.html"):
    contribution = get_object_or_404(Contribution, pk=id)
       
    if request.user.has_perm('contributions.view_contribution', contribution):
        return render_to_response(template_name, {'contribution': contribution}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
