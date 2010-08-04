from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Count

from base.http import Http403
from directories.models import Directory
from directories.forms import DirectoryForm
from perms.models import ObjectPermission
from perms.utils import get_notice_recipients
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType

try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="directories/view.html"):
    if not slug: return HttpResponseRedirect(reverse('directory.search'))
    directory = get_object_or_404(Directory, slug=slug)
    
    if request.user.has_perm('directories.view_directory', directory):
        log_defaults = {
            'event_id' : 435000,
            'event_data': '%s (%d) viewed by %s' % (directory._meta.object_name, directory.pk, request.user),
            'description': '%s viewed' % directory._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': directory,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="directories/search.html"):
    query = request.GET.get('q', None)
    directories = Directory.objects.search(query, user=request.user)

    log_defaults = {
        'event_id' : 434000,
        'event_data': '%s searched by %s' % ('Directory', request.user),
        'description': '%s searched' % 'Directory',
        'user': request.user,
        'request': request,
        'source': 'directories'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'directories':directories}, 
        context_instance=RequestContext(request))

def print_view(request, slug, template_name="directories/print-view.html"):
    directory = get_object_or_404(Directory, slug=slug)    

    log_defaults = {
        'event_id' : 435001,
        'event_data': '%s (%d) viewed by %s' % (directory._meta.object_name, directory.pk, request.user),
        'description': '%s viewed - print view' % directory._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': directory,
    }
    EventLog.objects.log(**log_defaults)
       
    if request.user.has_perm('directories.view_directory', directory):
        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=DirectoryForm, template_name="directories/edit.html"):
    directory = get_object_or_404(Directory, pk=id)

    if request.user.has_perm('directories.change_directory', directory):    
        if request.method == "POST":

            form = form_class(request.user, request.POST, instance=directory)

            if form.is_valid():
                directory = form.save(commit=False)

                # remove all permissions on the object
                ObjectPermission.objects.remove_all(directory)
                # assign new permissions
                user_perms = form.cleaned_data['user_perms']
                if user_perms:
                    ObjectPermission.objects.assign(user_perms, directory)  
                # assign creator permissions
                ObjectPermission.objects.assign(directory.creator, directory)
                
                directory.save()

                log_defaults = {
                    'event_id' : 432000,
                    'event_data': '%s (%d) edited by %s' % (directory._meta.object_name, directory.pk, request.user),
                    'description': '%s edited' % directory._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': directory,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.INFO, 'Successfully updated %s' % directory)
                
                # send notification to administrators
                # commenting out - there is no notification on edit in T4
#                if notification:
#                    extra_context = {
#                        'object': directory,
#                        'request': request,
#                    }
#                    admins = get_administrators()
#                    #admins = [request.user]
#                    #notification.send(get_administrators(),'directory_edited', extra_context)
#                    notification.send(admins,'directory_edited', extra_context)
                                                                             
                return HttpResponseRedirect(reverse('directory', args=[directory.slug]))             
        else:
            form = form_class(request.user, instance=directory)

        return render_to_response(template_name, {'directory': directory, 'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="directories/edit-meta.html"):

    # check permission
    directory = get_object_or_404(Directory, pk=id)
    if not request.user.has_perm('directories.change_directory', directory):
        raise Http403

    defaults = {
        'title': directory.get_title(),
        'description': directory.get_description(),
        'keywords': directory.get_keywords(),
    }
    directory.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=directory.meta)
        if form.is_valid():
            directory.meta = form.save() # save meta
            directory.save() # save relationship
            
            messages.add_message(request, messages.INFO, 'Successfully updated meta for %s' % directory)
             
            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))
    else:
        form = form_class(instance=directory.meta)

    return render_to_response(template_name, {'directory': directory, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=DirectoryForm, template_name="directories/add.html"):
    if request.user.has_perm('directories.add_directory'):
        if request.method == "POST":
            form = form_class(request.user, request.POST)
            if form.is_valid():           
                directory = form.save(commit=False)
                # set up the user information
                directory.creator = request.user
                directory.creator_username = request.user.username
                directory.owner = request.user
                directory.owner_username = request.user.username
                directory.save() # get pk

                # assign permissions for selected users
                user_perms = form.cleaned_data['user_perms']
                if user_perms: ObjectPermission.objects.assign(user_perms, directory)
                # assign creator permissions
                ObjectPermission.objects.assign(directory.creator, directory)

                directory.save() # update search-index w/ permissions
 
                log_defaults = {
                    'event_id' : 431000,
                    'event_data': '%s (%d) added by %s' % (directory._meta.object_name, directory.pk, request.user),
                    'description': '%s added' % directory._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': directory,
                }
                EventLog.objects.log(**log_defaults)
                
                messages.add_message(request, messages.INFO, 'Successfully added %s' % directory)
                
                # send notification to administrators
                # get admin notice recipients
                recipients = get_notice_recipients('module', 'directories', 'directoryrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': directory,
                            'request': request,
                        }
                        #notification.send(get_administrators(),'directory_added', extra_context)
                        notification.send_emails(recipients,'directory_added', extra_context)
                    
                return HttpResponseRedirect(reverse('directory', args=[directory.slug]))
        else:
            form = form_class(request.user)
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def delete(request, id, template_name="directories/delete.html"):
    directory = get_object_or_404(Directory, pk=id)

    if request.user.has_perm('directories.delete_directory'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 433000,
                'event_data': '%s (%d) deleted by %s' % (directory._meta.object_name, directory.pk, request.user),
                'description': '%s deleted' % directory._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': directory,
            }
            
            EventLog.objects.log(**log_defaults)

            messages.add_message(request, messages.INFO, 'Successfully deleted %s' % directory)

            # send notification to administrators
            recipients = get_notice_recipients('module', 'directories', 'directoryrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': directory,
                        'request': request,
                    }
                    notification.send_emails(recipients,'directory_deleted', extra_context)
                            
            directory.delete()
                                    
            return HttpResponseRedirect(reverse('directory.search'))
    
        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403


@staff_member_required
def directories_report(request):
    stats= EventLog.objects.filter(event_id=435000)\
                    .values('content_type', 'object_id', 'headline')\
                    .annotate(count=Count('pk'))\
                    .order_by('-count')
    for item in stats:
        ct = ContentType.objects.get_for_id(item['content_type'])
        assert ct.model_class() == Directory
        try:
            directory = Directory.objects.get(pk=item['object_id'])
            item['directory'] = directory
            item['per_day'] = item['count'] * 1.0 / directory.age().days
        except Directory.DoesNotExist:
            pass
        
    return render_to_response('reports/directories.html', 
            {'stats': stats}, 
            context_instance=RequestContext(request))
