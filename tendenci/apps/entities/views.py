from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.http import Http403
from tendenci.apps.entities.models import Entity
from tendenci.apps.entities.forms import EntityForm
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import has_perm, update_perms_and_save, get_query_filters


def index(request, id=None, template_name="entities/view.html"):
    if not id: return HttpResponseRedirect(reverse('entity.search'))
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.view_entity',entity):
        EventLog.objects.log(instance=entity)

        return render_to_response(template_name, {'entity': entity},
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="entities/search.html"):
    filters = get_query_filters(request.user, 'entities.view_entity')
    entities = Entity.objects.filter(filters).distinct()

    EventLog.objects.log()

    return render_to_response(template_name, {'entities':entities},
        context_instance=RequestContext(request))

def print_view(request, id, template_name="entities/print-view.html"):
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.view_entity',entity):
        EventLog.objects.log(instance=entity)

        return render_to_response(template_name, {'entity': entity},
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=EntityForm, template_name="entities/add.html"):
    if has_perm(request.user,'entities.add_entity'):
        if request.method == "POST":
            form = form_class(request.POST, user=request.user)
            if form.is_valid():
                entity = form.save(commit=False)

                # update all permissions and save the model
                entity = update_perms_and_save(request, form, entity)

                messages.add_message(request, messages.SUCCESS, _('Successfully added %(e)s' % { 'e': entity }))

                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))
        else:
            form = form_class(user=request.user)

        return render_to_response(template_name, {'form':form},
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit(request, id, form_class=EntityForm, template_name="entities/edit.html"):
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.change_entity',entity):
        if request.method == "POST":
            form = form_class(request.POST, instance=entity, user=request.user)
            if form.is_valid():
                entity = form.save(commit=False)

                # update all permissions and save the model
                entity = update_perms_and_save(request, form, entity)

                return HttpResponseRedirect(reverse('entity', args=[entity.pk]))
        else:
            form = form_class(instance=entity, user=request.user)

        return render_to_response(template_name, {'entity': entity, 'form':form},
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def delete(request, id, template_name="entities/delete.html"):
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.delete_entity'):
        if request.method == "POST":
            messages.add_message(request, messages.SUCCESS, _('Successfully deleted %(e)s' % { 'e' : entity }))
            entity.delete()

            return HttpResponseRedirect(reverse('entity.search'))

        return render_to_response(template_name, {'entity': entity},
            context_instance=RequestContext(request))
    else:
        raise Http403
