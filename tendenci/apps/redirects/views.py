from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.redirects.models import Redirect
from tendenci.apps.redirects.forms import RedirectForm
from tendenci.apps.redirects import dynamic_urls


@login_required
def search(request, template_name="redirects/search.html"):
    """
    This page lists out all redirects from newest to oldest.
    """
    query = request.GET.get('q', None)
    
    # check permission - users without the add or change premissions don't need to see it
    if not any([has_perm(request.user, 'redirects.add_redirect'),
                has_perm(request.user,'redirects.change_redirect')]):
        raise Http403
    
    redirects = Redirect.objects.all()

    if query:
        redirects = redirects.filter(Q(from_app__icontains=query) |
                                     Q(from_url__icontains=query) |
                                     Q(to_url__icontains=query) |
                                     Q(http_status__icontains=query))

    redirects = redirects.order_by('-create_dt')

    return render_to_resp(request=request, template_name=template_name,
        context={'redirects': redirects})


@login_required
def add(request, form_class=RedirectForm, template_name="redirects/add.html"):

    # check permission
    if not has_perm(request.user, 'redirects.add_redirect'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            redirect = form.save(commit=False)
            redirect.save()  # get pk

            messages.add_message(request, messages.SUCCESS, _('Successfully added %(r)s' % {'r':redirect}))

            # reload the urls
            from imp import reload
            reload(dynamic_urls)

            return HttpResponseRedirect(reverse('redirects'))
    else:
        form = form_class()

    return render_to_resp(request=request,
                          template_name=template_name,
                          context={'form': form})

@login_required
def edit(request, id, form_class=RedirectForm, template_name="redirects/edit.html"):
    redirect = get_object_or_404(Redirect, pk=id)

    # check permission
    if not has_perm(request.user,'redirects.change_redirect'):
        raise Http403

    form = form_class(instance=redirect)

    if request.method == "POST":
        form = form_class(request.POST, instance=redirect)
        if form.is_valid():
            redirect = form.save(commit=False)
            redirect.save() # get pk

            messages.add_message(request, messages.SUCCESS, _('Successfully edited %(r)s' % {'r':redirect}))

            # reload the urls
            from imp import reload
            reload(dynamic_urls)

            return HttpResponseRedirect(reverse('redirects'))

    return render_to_resp(request=request,
                          template_name=template_name,
                          context={'redirect': redirect,'form':form,})

@login_required
def delete(request, id, template_name="redirects/delete.html"):
    redirect = get_object_or_404(Redirect, pk=id)

    # check permission
    if not has_perm(request.user,'redirects.delete_redirect'):
        raise Http403

    if request.method == "POST":
        messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(r)s' % {'r':redirect}))
        redirect.delete()
        return HttpResponseRedirect(reverse('redirects'))

    return render_to_resp(request=request, template_name=template_name,
        context={'redirect': redirect})

@login_required
def export(request, template_name="redirects/export.html"):
    """Export redirects"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        fields = [
            'from_url',
            'to_url',
            'http_status',
            'status',
            'uses_regex',
            'create_dt',
            'update_dt',
        ]
        export_id = run_export_task('redirects', 'redirect', fields)
        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })
