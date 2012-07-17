from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from base.http import Http403
from perms.utils import update_perms_and_save, get_query_filters, has_perm
from event_logs.models import EventLog
from site_settings.utils import get_setting
from tenants.models import Map, Kind, Tenant, Photo, Line
from tenants.forms import MapForm, KindForm, TenantForm, PhotoForm, LineForm


def tenants_maps(request, template_name="tenants/maps/search.html"):
    query = request.GET.get('q')

    if get_setting('site', 'global', 'searchindex') and query:
        maps = Map.objects.search(query, user=request.user).order_by('-create_dt')
    else:
        filters = get_query_filters(request.user, 'maps.view_tenant')
        maps = Map.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            maps = maps.select_related()

    EventLog.objects.log()
    return render_to_response(template_name, {'maps': maps},
        context_instance=RequestContext(request))


def tenants_maps_detail(request, slug=u'', template_name='tenants/maps/detail.html'):
    from django.contrib.contenttypes.models import ContentType
    from tagging.models import TaggedItem

    if not slug:
        return HttpResponseRedirect(reverse('tenants.maps'))

    map = get_object_or_404(Map, slug=slug)

    if not has_perm(request.user, 'tenants.view_map', map):
        raise Http403

    EventLog.objects.log(instance=map)

    ct_tenant = ContentType.objects.get_for_model(Tenant)
    tags = TaggedItem.objects.filter(
        content_type=ct_tenant).values_list('tag__name', flat=True).distinct()

    tenants_by_tag = []
    for tag in tags:

        tenants = TaggedItem.objects.get_by_model(Tenant, tag).filter(
            map=map, status=True, status_detail='active')

        if tenants:
            tenants_by_tag.append({
                'tag_name': tag,
                'tenants': tenants
            })

    tenants = Tenant.objects.filter(tags='')
    if tenants:
        tenants_by_tag.append({
            'tag_name': u'',
            'tenants': tenants
        })

    return render_to_response(template_name, {'map': map, 'tenants_by_tag': tenants_by_tag},
        context_instance=RequestContext(request))


@login_required
def tenants_maps_add(request, template_name="tenants/maps/add.html"):
    if not has_perm(request.user, 'tenants.add_map'):
        return Http403

    if request.method == "POST":
        form = MapForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            map = form.save(commit=False)
            map = update_perms_and_save(request, form, map)

            EventLog.objects.log(**{
                'event_id': 9999000,
                'event_data': '%s (%d) added by %s' % (map._meta.object_name, map.pk, request.user),
                'description': '%s added' % map._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': map,
            })

            messages.add_message(request, messages.INFO, _('Successfully added %s' % map))
            return HttpResponseRedirect(reverse('tenants.maps'))
    else:
        form = MapForm(user=request.user)

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def tenants_maps_edit(request, pk=None, template_name="tenants/maps/edit.html"):
    if not has_perm(request.user, 'tenants.change_map'):
        return Http403

    map = get_object_or_404(Map, pk=pk)

    if request.method == "POST":
        form = MapForm(request.POST, request.FILES, instance=map)

        if form.is_valid():
            map = form.save(commit=False)
            map = update_perms_and_save(request, form, map)

            EventLog.objects.log(**{
                'event_id': 9999000,
                'event_data': '%s (%d) changed by %s' % (map._meta.object_name, map.pk, request.user),
                'description': '%s changed' % map._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': map,
            })

            messages.add_message(request, messages.INFO, _('Successfully changed %s' % map))
            return HttpResponseRedirect(reverse('tenants.maps'))

    else:
        form = MapForm(instance=map)

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def tenants_maps_delete(request, pk, template_name="tenants/maps/delete.html"):
    map = get_object_or_404(Map, pk=pk)

    if has_perm(request.user, 'tenants.delete_map'):
        if request.method == "POST":

            EventLog.objects.log(**{
                'event_id': 9999500,
                'event_data': '%s (%d) deleted by %s' % (map._meta.object_name, map.pk, request.user),
                'description': '%s deleted' % map._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': map,
            })

            map.delete()
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % map)
            return HttpResponseRedirect(reverse('tenants.maps'))

        return render_to_response(template_name, {'map': map},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def tenants_add(request, pk=None, template_name="tenants/add.html"):

    if not has_perm(request.user, 'tenants.add_tenant'):
        return Http403

    map = get_object_or_404(Map, pk=pk)

    if not map:
        messages.add_message(request, messages.INFO, _('Please select a Map.'))
        return HttpResponseRedirect(reverse('tenants.maps'))

    PhotoFormSet = modelformset_factory(Photo, form=PhotoForm, extra=1)
    LineFormSet = modelformset_factory(Line, form=LineForm, extra=0)

    if request.method == "POST":
        form = TenantForm(request.POST)

        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix="photos")
        formset = LineFormSet(request.POST, prefix="lines")

        if form.is_valid() and photo_formset.is_valid():
            tenant = form.save(commit=False)
            tenant = update_perms_and_save(request, form, tenant)

            photos = photo_formset.save(commit=False)
            for photo in photos:
                photo.tenant = tenant
                photo.creator = request.user
                photo.owner = request.user
                photo.save()

            points = formset.save(commit=False)
            for point in points:
                point.tenant = tenant
                point.save()

            messages.add_message(request, messages.INFO, 'Successfully added %s' % tenant)
            return HttpResponseRedirect(reverse('tenants.maps', args=[map.slug]))
    else:
        form = TenantForm(initial={"map": map})

        photo_formset = PhotoFormSet(queryset=Photo.objects.none(), prefix="photos")
        formset = LineFormSet(queryset=Line.objects.none(), prefix="lines")

    return render_to_response(template_name, {
        'map': map,
        'photo_formset': photo_formset,
        'formset': formset,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def tenants_edit(request, pk, template_name="tenants/edit.html"):
    if not has_perm(request.user, 'tenants.change_tenant'):
        return Http403

    tenant = get_object_or_404(Tenant, pk=pk)

    PhotoFormSet = modelformset_factory(Photo, form=PhotoForm, extra=1)
    LineFormSet = inlineformset_factory(Tenant, Line, extra=0)

    if request.method == "POST":
        form = TenantForm(request.POST, instance=tenant)

        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix="photos")
        formset = LineFormSet(request.POST, instance=tenant, queryset=Line.objects.none(), prefix="lines")

        if all((form.is_valid(), formset.is_valid(), photo_formset.is_valid())):

            tenant = form.save(commit=False)
            tenant = update_perms_and_save(request, form, tenant)

            photos = photo_formset.save(commit=False)

            for photo in photos:
                photo.tenant = tenant
                photo.creator = request.user
                photo.owner = request.user
                photo.save()

            if formset.total_form_count() > 1:
                tenant.line_set.all().delete()
                formset.save()

            messages.add_message(request, messages.INFO, _('Successfully updated %s' % tenant))
            return redirect('tenants.maps', tenant.map.slug)
    else:
        form = TenantForm(instance=tenant)
        photo_formset = PhotoFormSet(queryset=Photo.objects.filter(tenant=tenant), prefix="photos")
        formset = LineFormSet(instance=tenant, queryset=Line.objects.none(), prefix="lines")

    return render_to_response(template_name, {
        'photo_formset': photo_formset,
        'formset': formset,
        'form': form,
        'tenant': tenant,
        'map': tenant.map,
    }, context_instance=RequestContext(request))


@login_required
def tenants_delete(request, pk, template_name="tenants/delete.html"):
    tenant = get_object_or_404(Tenant, pk=pk)

    if has_perm(request.user, 'tenants.delete_tenant'):
        if request.method == "POST":

            EventLog.objects.log(**{
                'event_id': 9999500,
                'event_data': '%s (%d) deleted by %s' % (tenant._meta.object_name, tenant.pk, request.user),
                'description': '%s deleted' % tenant._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': tenant,
            })

            tenant.delete()
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % tenant)

            return HttpResponseRedirect(reverse('tenants.maps'))

        return render_to_response(template_name, {'tenant': tenant},
            context_instance=RequestContext(request))
    else:
        raise Http403


def tenants(request, template_name="tenants/search.html"):
    """
    Search/browse through all tenants, regardless of which map
    they're associated with.
    """

    query = request.GET.get('q')

    if get_setting('site', 'global', 'searchindex') and query:
        tenants = Tenant.objects.search(query, user=request.user).order_by('-create_dt')
    else:
        filters = get_query_filters(request.user, 'tenants.view_tenant')
        tenants = Tenant.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            tenants = tenants.select_related()

    EventLog.objects.log(**{
        'event_id': 9999400,
        'event_data': '%s searched by %s' % ('Tenant', request.user),
        'description': '%s searched' % 'Tenant',
        'user': request.user,
        'request': request,
        'source': 'tenants'
    })

    return render_to_response(template_name, {'tenants': tenants},
        context_instance=RequestContext(request))


def tenants_detail(request, slug=u'', template_name="tenants/detail.html"):
    if not slug:
        return HttpResponseRedirect(reverse('tenants'))
    tenant = get_object_or_404(Tenant, slug=slug)

    if has_perm(request.user, 'tenants.view_tenant', tenant):
        log_defaults = {
            'event_id': 9999500,
            'event_data': '%s (%d) viewed by %s' % (tenant._meta.object_name, tenant.pk, request.user),
            'description': '%s viewed' % tenant._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': tenant,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'tenant': tenant},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def tenants_kinds(request, template_name='tenants/kinds/search.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenants.%s_tenant' % perm):
            return Http403

    kinds = Kind.objects.all()
    EventLog.objects.log()
    return render_to_response(template_name, {
        'kinds': kinds
    }, context_instance=RequestContext(request))


@login_required
def tenants_kinds_detail(request, pk=None, template_name='tenants/kinds/detail.html'):
    if not pk:
        return HttpResponseRedirect(reverse('tenants.maps'))

    kind = get_object_or_404(Kind, pk=pk)

    if not has_perm(request.user, 'tenants.edit_tenant', map):
        raise Http403

    EventLog.objects.log(instance=kind)
    return render_to_response(template_name, {'kind': kind},
        context_instance=RequestContext(request))


@login_required
def tenants_kinds_add(request, pk=None, template_name='tenants/kinds/add.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenants.%s_tenant' % perm):
            return Http403

    if not has_perm(request.user, 'tenants.add_tenant'):
        return Http403

    if request.method == "POST":
        form = KindForm(request.POST)
        if form.is_valid():
            kind = form.save()
            EventLog.objects.log(instance=kind)
            messages.add_message(request, messages.INFO, _('Successfully added %s' % kind))
            return HttpResponseRedirect(reverse('tenants.kinds.detail', args=[kind.pk]))
    else:
        form = KindForm()

    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))


@login_required
def tenants_kinds_edit(request, pk=None, template_name='tenants/kinds/edit.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenants.%s_tenant' % perm):
            return Http403

    kind = get_object_or_404(Kind, pk=pk)

    if request.method == "POST":
        form = KindForm(request.POST, instance=kind)

        if form.is_valid():
            kind = form.save()
            EventLog.objects.log(instance=kind)
            messages.add_message(request, messages.INFO, _('Successfully changed %s' % kind))
            return HttpResponseRedirect(reverse('tenants.kinds.detail', args=[kind.pk]))
    else:
        form = KindForm(instance=kind)

    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))


@login_required
def tenants_kinds_delete(request, pk=None, template_name='tenants/kinds/delete.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenants.%s_tenant' % perm):
            return Http403

    kind = get_object_or_404(Kind, pk=pk)

    if request.method == "POST":
        EventLog.objects.log(instance=kind)
        kind.delete()
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % kind)
        return HttpResponseRedirect(reverse('tenants.kinds'))

    return render_to_response(template_name, {'kind': kind},
        context_instance=RequestContext(request))
