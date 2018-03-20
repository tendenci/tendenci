from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import simplejson as json

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.decorators import is_enabled
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.pages.models import Page
from tendenci.apps.exports.utils import run_export_task

from tendenci.apps.navs.models import Nav
from tendenci.apps.navs.forms import NavForm, PageSelectForm


@is_enabled('navs')
@login_required
def search(request, template_name="navs/search.html"):
    return redirect(reverse('admin:navs_nav_changelist'))
    # query = request.GET.get('q', None)

    # filters = get_query_filters(request.user, 'navs.view_nav')
    # navs = Nav.objects.filter(filters).distinct()
    # if query:
    #     navs = navs.filter(Q(title__icontains=query)|Q(description__icontains=query))

    # EventLog.objects.log()

    # return render_to_resp(request=request, template_name=template_name,
    #     context={'navs':navs})


@is_enabled('navs')
@login_required
def detail(request, id, template_name="navs/detail.html"):
    return redirect(reverse('admin:navs_nav_change', args=[id]))
    # nav = get_object_or_404(Nav, id=id)

    # if not has_view_perm(request.user, 'navs.view_nav', nav):
    #     raise Http403

    # EventLog.objects.log(instance=nav)

    # return render_to_resp(request=request, template_name=template_name,
    #     context={'current_nav':nav})


@is_enabled('navs')
@login_required
def add(request, form_class=NavForm, template_name="navs/add.html"):
    return redirect(reverse('admin:navs_nav_add'))
    # if not has_perm(request.user, 'navs.add_nav'):
    #     raise Http403

    # if request.method == "POST":
    #     form = form_class(request.POST, user=request.user)
    #     if form.is_valid():
    #         nav = form.save(commit=False)
    #         nav = update_perms_and_save(request, form, nav)

    #         messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % nav)
    #         return redirect('navs.edit_items', id=nav.id)
    # else:
    #     form = form_class(user=request.user)

    # return render_to_resp(request=request, template_name=template_name,
    #     context={'form':form})


@is_enabled('navs')
@login_required
def edit(request, id, form_class=NavForm, template_name="navs/edit.html"):
    return redirect(reverse('admin:navs_nav_change', args=[id]))
    # nav = get_object_or_404(Nav, id=id)
    # if not has_perm(request.user, 'navs.change_nav', nav):
    #     raise Http403

    # if request.method == "POST":
    #     form = form_class(request.POST, instance=nav, user=request.user)
    #     if form.is_valid():
    #         nav = form.save(commit=False)
    #         nav = update_perms_and_save(request, form, nav)
    #         cache_nav(nav)

    #         messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % nav)
    #         return redirect('navs.edit_items', id=nav.id)
    # else:
    #     form = form_class(user=request.user, instance=nav)

    # return render_to_resp(request=request, template_name=template_name,
    #     context={'form':form, 'current_nav':nav})


@is_enabled('navs')
@login_required
def edit_items(request, id, template_name="navs/nav_items.html"):
    return redirect(reverse('admin:navs_nav_change', args=[id]))
    # nav = get_object_or_404(Nav, id=id)
    # if not has_perm(request.user, 'navs.change_nav', nav):
    #     raise Http403

    # ItemFormSet = modelformset_factory(NavItem,
    #                     form=ItemForm,
    #                     extra=0,
    #                     can_delete=True)
    # page_select = PageSelectForm()

    # if request.method == "POST":
    #     formset = ItemFormSet(request.POST)
    #     if formset.is_valid():
    #         #delete old nav items
    #         nav.navitem_set.all().delete()
    #         items = formset.save(commit=False)
    #         # update or create nav items
    #         for item in items:
    #             item.nav = nav
    #             item.save()
    #         cache_nav(nav)
    #         messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % nav)
    #         if nav.pk == 1:  # the main nav has id 1 in the npo defaults fixture
    #             checklist_update('update-nav')

    #         EventLog.objects.log(instance=nav)

    #         redirect_to = request.GET.get('next', '')
    #         if redirect_to:
    #             return HttpResponseRedirect(redirect_to)
    #         else:
    #             return redirect('navs.detail', id=nav.id)
    # else:
    #     formset = ItemFormSet(queryset=nav.navitem_set.all().order_by('position'))

    # return render_to_resp(request=request, template_name=template_name,
    #     context={'page_select':page_select, 'formset':formset, 'current_nav':nav})


@is_enabled('navs')
@login_required
def delete(request, id, template_name="navs/delete.html"):
    nav = get_object_or_404(Nav, pk=id)

    if has_perm(request.user,'navs.delete_nav'):
        if request.method == "POST":
            messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(nav)s' % {'nav': nav}))

            nav.delete()
            return HttpResponseRedirect(reverse('navs.search'))

        return render_to_resp(request=request, template_name=template_name,
            context={'current_nav': nav})
    else:
        raise Http403


@is_enabled('navs')
@login_required
def page_select(request, form_class=PageSelectForm):
    if not request.user.profile.is_superuser:
        raise Http403

    if request.method=="POST":
        form = form_class(request.POST)
        if form.is_valid():
            pages = form.cleaned_data['pages']
            infos = []
            for page in pages:
                infos.append({
                    "url": page.get_absolute_url(),
                    "label": page.title,
                    "id": page.id,
                })
            return HttpResponse(json.dumps({
                "pages": infos,
            }), content_type="text/plain")
    return HttpResponse(json.dumps({
                "error": True
            }), content_type="text/plain")


@is_enabled('navs')
@login_required
def export(request, template_name="navs/export.html"):
    """Export Navs"""
    if not request.user.is_superuser:
        raise Http403

    if request.method == 'POST':
        export_id = run_export_task('navs', 'nav', [])

        EventLog.objects.log()

        return redirect('export.status', export_id)

    return render_to_resp(request=request, template_name=template_name, context={
    })


def get_item_attrs(request):
    item_id = int(request.GET.get('item_id', 0))

    try:
        item = Page.objects.get(pk=item_id)
    except Page.DoesNotExist:
        item = None

    if item:
        data = {
            'status': 'ok',
            'label': item.title,
            'title': item.title,
            'url': '/' + item.slug + '/'
        }

    else:
        data = {'status': 'fail'}

    return HttpResponse(json.dumps(data))
