from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.http import Http403
from tendenci.core.perms.utils import has_perm, get_query_filters
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.theme.shortcuts import themed_response as render_to_response
from tendenci.core.exports.utils import run_export_task

from tendenci.apps.redirects.models import Redirect
from tendenci.apps.redirects.forms import RedirectForm
from tendenci.apps.redirects import dynamic_urls


@login_required
def search(request, template_name="redirects/search.html"):
    """
    This page lists out all redirects from newest to oldest.
    If a search index is available, this page will also
    have the option to search through redirects.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        redirects = Redirect.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'redirects.add_redirect')
        redirects = Redirect.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            redirects = redirects.select_related()
        redirects = redirects.order_by('-create_dt')

    # check permission
    if not has_perm(request.user, 'redirects.add_redirect'):
        raise Http403

    return render_to_response(template_name, {'redirects': redirects},
        context_instance=RequestContext(request))


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
            reload(dynamic_urls)

            return HttpResponseRedirect(reverse('redirects'))
    else:
        form = form_class()

    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=RedirectForm, template_name="redirects/edit.html"):
    redirect = get_object_or_404(Redirect, pk=id)

    # check permission
    if not has_perm(request.user,'redirects.add_redirect'):
        raise Http403

    form = form_class(instance=redirect)

    if request.method == "POST":
        form = form_class(request.POST, instance=redirect)
        if form.is_valid():
            redirect = form.save(commit=False)
            redirect.save() # get pk

            messages.add_message(request, messages.SUCCESS, _('Successfully edited %(r)s' % {'r':redirect}))

            # reload the urls
            reload(dynamic_urls)

            return HttpResponseRedirect(reverse('redirects'))

    return render_to_response(template_name, {'redirect': redirect,'form':form}, context_instance=RequestContext(request))

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

    return render_to_response(template_name, {'redirect': redirect},
        context_instance=RequestContext(request))

@login_required
def export(request, template_name="redirects/export.html"):
    """Export redirects"""

    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        # initilize initial values
        file_name = "redirects.csv"
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

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
