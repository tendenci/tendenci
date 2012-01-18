from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from base.http import Http403
from perms.utils import update_perms_and_save, has_perm
from event_logs.models import EventLog
from perms.utils import is_admin

from lots.models import Lot, Map, Line
from lots.forms import LotForm, MapForm, LineForm

try:
    from notification import models as notification
except:
    notification = None

def index(request, template_name="lots/detail.html"):
    return HttpResponseRedirect(reverse('lots.search'))
    
def map_selection(request, template_name="lots/maps/search.html"):
    query = request.GET.get('q', None)
    maps = Map.objects.search(query, user=request.user)
    maps = maps.order_by('-create_dt')

    log_defaults = {
        'event_id' : 9999400,
        'event_data': '%s searched by %s' % ('Map', request.user),
        'description': '%s searched' % 'Map',
        'user': request.user,
        'request': request,
        'source': 'maps'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {
        'maps':maps
    }, context_instance=RequestContext(request))

@login_required
def map_add(request, template_name="lots/maps/add.html"):
    if not has_perm(request.user, 'lots.add_map'):
        return Http403
        
    if request.method == "POST":
        form = MapForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            map = form.save(commit=False)
            map = update_perms_and_save(request, form, map)
            
            log_defaults = {
                'event_id' : 9999000,
                'event_data': '%s (%d) added by %s' % (map._meta.object_name, map.pk, request.user),
                'description': '%s added' % map._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': map,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.INFO, 'Successfully added %s' % map)
    else:
        form = MapForm(user=request.user)
        
    return render_to_response(template_name, {
        'form':form,
    }, context_instance=RequestContext(request))

@login_required    
def add(request, map_id=None, template_name="lots/add.html"):
    if not has_perm(request.user, 'lots.add_lot'):
        return Http403
    
    if map_id:
        map_instance = Map.objects.get(pk=map_id)
    else:
        map_instance = None
        
    LineFormSet = modelformset_factory(Line, form=LineForm)
    
    if request.method == "POST":
        form = LotForm(request.POST)
        formset = LineFormSet(request.POST, queryset=Line.objects.none(), prefix="lines")
        if False not in (form.is_valid(), formset.is_valid()):
            lot = form.save(commit=False)
            lot = update_perms_and_save(request, form, lot)
            points = formset.save(commit=False)
            for point in points:
                point.lot = lot
                point.save()
            messages.add_message(request, messages.INFO, 'Successfully added %s' % lot)
            return redirect('lots.detail', lot.pk)
    else:
        form = LotForm(initial={"map":map_instance})
        formset = LineFormSet(queryset=Line.objects.none(), prefix="lines")
        
    return render_to_response(template_name, {
        'map': map_instance,
        'formset':formset,
        'form':form,
    }, context_instance=RequestContext(request))

@login_required
def edit(request, pk, template_name="lots/edit.html"):
    if not has_perm(request.user, 'lots.change_lot'):
        return Http403
        
    lot = get_object_or_404(Lot, pk=pk)
    
    LineFormSet = inlineformset_factory(Lot, Line)
    
    if request.method == "POST":
        form = LotForm(request.POST, instance=lot)
        formset = LineFormSet(request.POST, instance=lot, prefix="lines")
        if False not in (form.is_valid(), formset.is_valid()):
            lot = form.save(commit=False)
            lot = update_perms_and_save(request, form, lot)
            points = formset.save()
            messages.add_message(request, messages.INFO, 'Successfully updated %s' % lot)
            return redirect('lots.detail', lot.pk)
    else:
        form = LotForm(instance=lot)
        formset = LineFormSet(instance=lot, prefix="lines")
    
    return render_to_response(template_name, {
        'formset':formset,
        'form':form,
        'lot':lot,
        'map':lot.map,
    }, context_instance=RequestContext(request))

def detail(request, pk=None, template_name="lots/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('lots.search'))
    lot = get_object_or_404(Lot, pk=pk)
    
    if has_perm(request.user, 'lots.view_lot', lot):
        log_defaults = {
            'event_id' : 9999500,
            'event_data': '%s (%d) viewed by %s' % (lot._meta.object_name, lot.pk, request.user),
            'description': '%s viewed' % lot._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': lot,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'lot': lot}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="lots/search.html"):
    query = request.GET.get('q', None)
    lots = Lot.objects.search(query, user=request.user)
    lots = lots.order_by('-create_dt')

    log_defaults = {
        'event_id' : 9999400,
        'event_data': '%s searched by %s' % ('Lot', request.user),
        'description': '%s searched' % 'Lot',
        'user': request.user,
        'request': request,
        'source': 'lots'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'lots':lots}, 
        context_instance=RequestContext(request))
