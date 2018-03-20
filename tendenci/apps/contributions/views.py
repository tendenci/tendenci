from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.contributions.models import Contribution
from tendenci.apps.perms.utils import has_perm


@login_required
def index(request, id=None, template_name="contributions/view.html"):
    if not id: return HttpResponseRedirect(reverse('contribution.search'))
    contribution = get_object_or_404(Contribution, pk=id)

    if has_perm(request.user,'contributions.view_contribution',contribution):
        return render_to_resp(request=request, template_name=template_name,
            context={'contribution': contribution})
    else:
        raise Http403

@login_required
def search(request, template_name="contributions/search.html"):
    query = request.GET.get('q', None)
    if request.user.profile.is_superuser:
        contributions = Contribution.objects.all()
    else:
        contributions = Contribution.objects.filter(Q(creator=request.user) | Q(owner=request.user))

    if query:
        contributions = contributions.filter(Q(creator__username=query) | Q(owner__username=query) | Q(title__icontains=query))

    contributions = contributions.order_by('-create_dt')

    return render_to_resp(request=request, template_name=template_name,
        context={'contributions':contributions})

@login_required
def print_view(request, id, template_name="contributions/print-view.html"):
    contribution = get_object_or_404(Contribution, pk=id)

    if has_perm(request.user,'contributions.view_contribution',contribution):
        return render_to_resp(request=request, template_name=template_name,
            context={'contribution': contribution})
    else:
        raise Http403
