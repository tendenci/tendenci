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
from tenents.models import Map, Kind, Tenent, Photo, Line
from tenents.forms import MapForm, KindForm, TenentForm, PhotoForm, LineForm


def tenents_maps(request, template_name="tenents/maps/search.html"):
    query = request.GET.get('q')

    if get_setting('site', 'global', 'searchindex') and query:
        maps = Map.objects.search(query, user=request.user).order_by('-create_dt')
    else:
        filters = get_query_filters(request.user, 'maps.view_tenent')
        maps = Map.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            maps = maps.select_related()

    EventLog.objects.log()
    return render_to_response(template_name, {'maps': maps},
        context_instance=RequestContext(request))


def tenents_maps_detail(request, slug=u'', template_name='tenents/maps/detail_plot.html'):

    if not slug:
        return HttpResponseRedirect(reverse('tenents.maps'))

    map = get_object_or_404(Map, slug=slug)

    if not has_perm(request.user, 'tenents.view_map', map):
        raise Http403

    EventLog.objects.log(instance=map)
    tenents = Tenent.objects.filter(map=map, status=True, status_detail='active')

    return render_to_response(template_name, {'map': map, 'tenents': tenents},
        context_instance=RequestContext(request))


@login_required
def tenents_maps_add(request, template_name="tenents/maps/add.html"):
    if not has_perm(request.user, 'tenents.add_map'):
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
            return HttpResponseRedirect(reverse('tenents.maps'))
    else:
        form = MapForm(user=request.user)

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def tenents_maps_edit(request, pk=None, template_name="tenents/maps/edit.html"):
    if not has_perm(request.user, 'tenents.change_map'):
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
            return HttpResponseRedirect(reverse('tenents.maps'))

    else:
        form = MapForm(instance=map)

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def tenents_maps_delete(request, pk, template_name="tenents/maps/delete.html"):
    map = get_object_or_404(Map, pk=pk)

    if has_perm(request.user, 'tenents.delete_map'):
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
            return HttpResponseRedirect(reverse('tenents.maps'))

        return render_to_response(template_name, {'map': map},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def tenents_add(request, pk=None, template_name="tenents/add.html"):

    if not has_perm(request.user, 'tenents.add_tenent'):
        return Http403

    map = get_object_or_404(Map, pk=pk)

    if not map:
        messages.add_message(request, messages.INFO, _('Please select a Map.'))
        return HttpResponseRedirect(reverse('tenents.maps'))

    PhotoFormSet = modelformset_factory(Photo, form=PhotoForm, extra=1)
    LineFormSet = modelformset_factory(Line, form=LineForm, extra=0)

    if request.method == "POST":
        form = TenentForm(request.POST)

        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix="photos")
        formset = LineFormSet(request.POST, prefix="lines")

        if photo_formset.is_valid():
            tenent = form.save(commit=False)
            tenent = update_perms_and_save(request, form, tenent)

            photos = photo_formset.save(commit=False)
            for photo in photos:
                photo.tenent = tenent
                photo.creator = request.user
                photo.owner = request.user
                photo.save()

            points = formset.save(commit=False)
            for point in points:
                point.tenent = tenent
                point.save()

            messages.add_message(request, messages.INFO, 'Successfully added %s' % tenent)
            return HttpResponseRedirect(reverse('tenents.maps', args=[map.slug]))
    else:
        form = TenentForm(initial={"map": map})

        photo_formset = PhotoFormSet(queryset=Photo.objects.none(), prefix="photos")
        formset = LineFormSet(queryset=Line.objects.none(), prefix="lines")

    return render_to_response(template_name, {
        'map': map,
        'photo_formset': photo_formset,
        'formset': formset,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def tenents_edit(request, pk, template_name="tenents/edit.html"):
    if not has_perm(request.user, 'tenents.change_tenent'):
        return Http403

    tenent = get_object_or_404(Tenent, pk=pk)

    PhotoFormSet = modelformset_factory(Photo, form=PhotoForm, extra=1)
    LineFormSet = inlineformset_factory(Tenent, Line, extra=0)

    if request.method == "POST":
        form = TenentForm(request.POST, instance=tenent)

        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix="photos")
        formset = LineFormSet(request.POST, instance=tenent, queryset=Line.objects.none(), prefix="lines")

        if all((form.is_valid(), formset.is_valid(), photo_formset.is_valid())):

            tenent = form.save(commit=False)
            tenent = update_perms_and_save(request, form, tenent)

            photos = photo_formset.save(commit=False)

            for photo in photos:
                photo.tenent = tenent
                photo.creator = request.user
                photo.owner = request.user
                photo.save()

            if formset.total_form_count() > 1:
                tenent.line_set.all().delete()
                formset.save()

            messages.add_message(request, messages.INFO, _('Successfully updated %s' % tenent))
            return redirect('tenents.maps', tenent.map.slug)
    else:
        form = TenentForm(instance=tenent)
        photo_formset = PhotoFormSet(queryset=Photo.objects.filter(tenent=tenent), prefix="photos")
        formset = LineFormSet(instance=tenent, queryset=Line.objects.none(), prefix="lines")

    print 'photo_formset', photo_formset

    return render_to_response(template_name, {
        'photo_formset': photo_formset,
        'formset': formset,
        'form': form,
        'tenent': tenent,
        'map': tenent.map,
    }, context_instance=RequestContext(request))


@login_required
def tenents_delete(request, pk, template_name="tenents/delete.html"):
    tenent = get_object_or_404(Tenent, pk=pk)

    if has_perm(request.user, 'tenents.delete_tenent'):
        if request.method == "POST":

            EventLog.objects.log(**{
                'event_id': 9999500,
                'event_data': '%s (%d) deleted by %s' % (tenent._meta.object_name, tenent.pk, request.user),
                'description': '%s deleted' % tenent._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': tenent,
            })

            tenent.delete()
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % tenent)

            return HttpResponseRedirect(reverse('tenents.maps'))

        return render_to_response(template_name, {'tenent': tenent},
            context_instance=RequestContext(request))
    else:
        raise Http403


def tenents(request, template_name="tenents/search.html"):
    """
    Search/browse through all tenents, regardless of which map
    they're associated with.
    """

    query = request.GET.get('q')

    if get_setting('site', 'global', 'searchindex') and query:
        tenents = Tenent.objects.search(query, user=request.user).order_by('-create_dt')
    else:
        filters = get_query_filters(request.user, 'tenents.view_tenent')
        tenents = Tenent.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            tenents = tenents.select_related()

    EventLog.objects.log(**{
        'event_id': 9999400,
        'event_data': '%s searched by %s' % ('Tenent', request.user),
        'description': '%s searched' % 'Tenent',
        'user': request.user,
        'request': request,
        'source': 'tenents'
    })

    return render_to_response(template_name, {'tenents': tenents},
        context_instance=RequestContext(request))


def tenents_detail(request, slug=u'', template_name="tenents/detail.html"):
    if not slug:
        return HttpResponseRedirect(reverse('tenents'))
    tenent = get_object_or_404(Tenent, slug=slug)

    if has_perm(request.user, 'tenents.view_tenent', tenent):
        log_defaults = {
            'event_id': 9999500,
            'event_data': '%s (%d) viewed by %s' % (tenent._meta.object_name, tenent.pk, request.user),
            'description': '%s viewed' % tenent._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': tenent,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'tenent': tenent},
            context_instance=RequestContext(request))
    else:
        raise Http403


@login_required
def tenents_kinds(request, template_name='tenents/kinds/search.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenents.%s_tenent' % perm):
            return Http403

    kinds = Kind.objects.all()
    EventLog.objects.log()
    return render_to_response(template_name, {
        'kinds': kinds
    }, context_instance=RequestContext(request))


@login_required
def tenents_kinds_detail(request, pk=None, template_name='tenents/kinds/detail.html'):
    if not pk:
        return HttpResponseRedirect(reverse('tenents.maps'))

    kind = get_object_or_404(Kind, pk=pk)

    if not has_perm(request.user, 'tenents.edit_tenent', map):
        raise Http403

    EventLog.objects.log(instance=kind)
    return render_to_response(template_name, {'kind': kind},
        context_instance=RequestContext(request))


@login_required
def tenents_kinds_add(request, pk=None, template_name='tenents/kinds/add.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenents.%s_tenent' % perm):
            return Http403

    if not has_perm(request.user, 'tenents.add_tenent'):
        return Http403

    if request.method == "POST":
        form = KindForm(request.POST)
        if form.is_valid():
            kind = form.save()
            EventLog.objects.log(instance=kind)
            messages.add_message(request, messages.INFO, _('Successfully added %s' % kind))
            return HttpResponseRedirect(reverse('tenents.kinds.detail', args=[kind.pk]))
    else:
        form = KindForm()

    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))


@login_required
def tenents_kinds_edit(request, pk=None, template_name='tenents/kinds/edit.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenents.%s_tenent' % perm):
            return Http403

    kind = get_object_or_404(Kind, pk=pk)

    if request.method == "POST":
        form = KindForm(request.POST, instance=kind)

        if form.is_valid():
            kind = form.save()
            EventLog.objects.log(instance=kind)
            messages.add_message(request, messages.INFO, _('Successfully changed %s' % kind))
            return HttpResponseRedirect(reverse('tenents.kinds.detail', args=[kind.pk]))
    else:
        form = KindForm(instance=kind)

    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))


@login_required
def tenents_kinds_delete(request, pk=None, template_name='tenents/kinds/delete.html'):

    for perm in ['add', 'change', 'delete']:
        if not has_perm(request.user, 'tenents.%s_tenent' % perm):
            return Http403

    kind = get_object_or_404(Kind, pk=pk)

    if request.method == "POST":
        EventLog.objects.log(instance=kind)
        kind.delete()
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % kind)
        return HttpResponseRedirect(reverse('tenents.kinds'))

    return render_to_response(template_name, {'kind': kind},
        context_instance=RequestContext(request))
