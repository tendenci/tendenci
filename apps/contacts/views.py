from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from site_settings.utils import get_setting
from contacts.models import Contact
from contacts.forms import ContactForm
from perms.object_perms import ObjectPermission
from perms.utils import has_perm, has_view_perm, get_query_filters

def details(request, id=None, template_name="contacts/view.html"):
    if not id: return HttpResponseRedirect(reverse('contacts'))
    contact = get_object_or_404(Contact, pk=id)
    
    if has_view_perm(request.user,'contacts.view_contact',contact):
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


def list(request, template_name="contacts/list.html"):
    if request.user.is_anonymous():
        raise Http403
    if not has_perm(request.user,'contacts.view_contact'):
        raise Http403

    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        contacts = Contact.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'contacts.view_contact')
        contacts = Contact.objects.filter(filters).distinct()
        if not request.user.is_anonymous():
            contacts = contacts.select_related()

    contacts = contacts.order_by('-create_dt')

    return render_to_response(template_name, {'contacts':contacts},
        context_instance=RequestContext(request))


def search(request):
    return HttpResponseRedirect(reverse('contacts'))


def print_view(request, id, template_name="contacts/print-view.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_view_perm(request.user,'contacts.view_contact',contact):
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=ContactForm, template_name="contacts/add.html"):
    if has_perm(request.user,'contacts.add_contact'):

        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():           
                contact = form.save(commit=False)
                # set up the user information
                contact.creator = request.user
                contact.creator_username = request.user.username
                contact.owner = request.user
                contact.owner_username = request.user.username
                contact.save()

                ObjectPermission.objects.assign(contact.creator, contact) 
                
                return HttpResponseRedirect(reverse('contact', args=[contact.pk]))
        else:
            form = form_class()
            print form_class()
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="contacts/delete.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_perm(request.user,'contacts.delete_contact'):   
        if request.method == "POST":
            contact.delete()
            return HttpResponseRedirect(reverse('contact.search'))
    
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403