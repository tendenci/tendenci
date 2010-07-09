from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from contacts.models import Contact
from contacts.forms import ContactForm
from perms.models import ObjectPermission
#from event_logs.models import EventLog
#from django.contrib.auth.models import AnonymousUser


def index(request, id=None, template_name="contacts/view.html"):
    if not id: return HttpResponseRedirect(reverse('contact.search'))
    contact = get_object_or_404(Contact, pk=id)
    
    if request.user.has_perm('contacts.view_contact', contact):
#        log_defaults = {
#            'event_id' : 587500,
#            'event_data': '%s (%d) viewed by %s' % (contact._meta.object_name, contact.pk, request.user),
#            'description': '%s viewed' % contact._meta.object_name,
#            'user': request.user,
#            'request': request,
#            'instance': contact,
#        }
#        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="contacts/search.html"):
    query = request.GET.get('q', None)
    contacts = Contact.objects.search(query, user=request.user)

#    log_defaults = {
#        'event_id' : 587400,
#        'event_data': '%s searched by %s' % ('Contact', request.user),
#        'description': '%s searched' % 'Contact',
#        'user': request.user,
#        'request': request,
#        'source': 'contacts'
#    }
#    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'contacts':contacts}, 
        context_instance=RequestContext(request))

def print_view(request, id, template_name="contacts/print-view.html"):
    contact = get_object_or_404(Contact, pk=id)    

#    log_defaults = {
#        'event_id' : 587500,
#        'event_data': '%s (%d) viewed by %s' % (contact._meta.object_name, contact.pk, request.user),
#        'description': '%s viewed' % contact._meta.object_name,
#        'user': request.user,
#        'request': request,
#        'instance': contact,
#    }
#    EventLog.objects.log(**log_defaults)
       
    if request.user.has_perm('contacts.view_contact', contact):
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def add(request, form_class=ContactForm, template_name="contacts/add.html"):
    if request.user.has_perm('contacts.add_contact'):

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
 
#                log_defaults = {
#                    'event_id' : 125114,
#                    'event_data': '%s (%d) added by %s' % (contact._meta.object_name, contact.pk, request.user),
#                    'description': '%s added' % contact._meta.object_name,
#                    'user': AnonymousUser(),
#                    'request': request,
#                    'instance': contact,
#                }
#                EventLog.objects.log(**log_defaults)
                               
                # assign permissions for selected users
#                user_perms = form.cleaned_data['user_perms']
#                if user_perms: ObjectPermission.objects.assign(user_perms, contact)
                
                # assign creator permissions
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

    if request.user.has_perm('contacts.delete_contact'):   
        if request.method == "POST":
#            log_defaults = {
#                'event_id' : 587300,
#                'event_data': '%s (%d) deleted by %s' % (contact._meta.object_name, contact.pk, request.user),
#                'description': '%s deleted' % contact._meta.object_name,
#                'user': request.user,
#                'request': request,
#                'instance': contact,
#            }
#            
#            EventLog.objects.log(**log_defaults)
            
            contact.delete()
                
            return HttpResponseRedirect(reverse('contact.search'))
    
        return render_to_response(template_name, {'contact': contact}, 
            context_instance=RequestContext(request))
    else:
        raise Http403