from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.entities.models import Entity
from tendenci.apps.entities.forms import EntityForm
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import has_perm, update_perms_and_save


@login_required
def index(request, id=None, template_name="entities/view.html"):
    if not id: return HttpResponseRedirect(reverse('entity.search'))
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.view_entity',entity):
        EventLog.objects.log(instance=entity)

        return render_to_resp(request=request, template_name=template_name,
            context={'entity': entity})
    else:
        raise Http403


@login_required
def search(request, template_name="entities/search.html"):
    filters = Entity.get_search_filter(request.user)
    entities = Entity.objects.all()
    if filters:
        entities = entities.filter(filters).distinct()

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name,
        context={'entities':entities})


@login_required
def print_view(request, id, template_name="entities/print-view.html"):
    entity = get_object_or_404(Entity, pk=id)

    if has_perm(request.user,'entities.view_entity',entity):
        EventLog.objects.log(instance=entity)

        return render_to_resp(request=request, template_name=template_name,
            context={'entity': entity})
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

        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})
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

        return render_to_resp(request=request, template_name=template_name,
            context={'entity': entity, 'form':form})
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

        return render_to_resp(request=request, template_name=template_name,
            context={'entity': entity})
    else:
        raise Http403
