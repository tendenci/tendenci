from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from contacts.models import Contact
from contacts.forms import ContactForm
from perms.object_perms import ObjectPermission
from perms.utils import has_perm

def index(request, id=None, template_name="contacts/view.html"):
    if not id: return HttpResponseRedirect(reverse('contact.search'))
    contact = get_object_or_404(Contact, pk=id)
    
    if has_perm(request.user,'contacts.view_contact',contact):
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="contacts/search.html"):
    if not has_perm(request.user,'contacts.view_contact'):
        raise Http403

    query = request.GET.get('q', None)
    contacts = Contact.objects.search(query, user=request.user)
    contacts = contacts.order_by('-create_dt')
    
    return render_to_response(template_name, {'contacts':contacts}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="contacts/print-view.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_perm(request.user,'contacts.view_contact',contact):
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