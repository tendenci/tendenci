from datetime import datetime, timedelta
from PIL import Image

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from site_settings.utils import get_setting
from base.http import Http403
from perms.utils import get_notice_recipients, update_perms_and_save
from perms.utils import (is_admin, has_perm)
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from theme.shortcuts import themed_response as render_to_response

from directories.models import Directory, DirectoryPricing
from directories.forms import DirectoryForm, DirectoryPricingForm
from directories.utils import directory_set_inv_payment

try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="directories/view.html"):
    if not slug: return HttpResponseRedirect(reverse('directory.search'))
    directory = get_object_or_404(Directory, slug=slug)
    
    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (directory.status_detail).lower() != 'active' and (not is_admin(request.user)):
        raise Http403
    
    if has_perm(request.user,'directories.view_directory',directory):
        log_defaults = {
            'event_id' : 445000,
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

    get = dict(request.GET)
    query = get.pop('q', [''])
    get.pop('page', None)  # pop page query string out; page ruins pagination
    query_extra = ['%s:%s' % (k,v[0]) for k,v in get.items() if v[0].strip()]
    query = '%s %s' % (''.join(query), ' '.join(query_extra))

    directories = Directory.objects.search(
        query, user=request.user).order_by('headline_exact')

    log_defaults = {
        'event_id' : 444000,
        'event_data': '%s searched by %s' % ('Directory', request.user),
        'description': '%s searched' % 'Directory',
        'user': request.user,
        'request': request,
        'source': 'directories'
    }
    EventLog.objects.log(**log_defaults)
    category = request.GET.get('category')
    try:
        category = int(category)
    except:
        category = 0
    categories, sub_categories = Directory.objects.get_categories(category=category)

    return render_to_response(template_name, {
        'directories':directories,
        'categories':categories,
        'sub_categories':sub_categories,
        }, 
        context_instance=RequestContext(request))

def print_view(request, slug, template_name="directories/print-view.html"):
    directory = get_object_or_404(Directory, slug=slug)    

    log_defaults = {
        'event_id' : 445001,
        'event_data': '%s (%d) viewed by %s' % (directory._meta.object_name, directory.pk, request.user),
        'description': '%s viewed - print view' % directory._meta.object_name,
        'user': request.user,
        'request': request,
        'instance': directory,
    }
    EventLog.objects.log(**log_defaults)
       
    if has_perm(request.user,'directories.view_directory',directory):
        return render_to_response(template_name, {'directory': directory}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def edit(request, id, form_class=DirectoryForm, template_name="directories/edit.html"):
    directory = get_object_or_404(Directory, pk=id)

    if not has_perm(request.user,'directories.change_directory',directory):  raise Http403 
    
    if request.method == "POST":

        form = form_class(request.POST, request.FILES, instance=directory, user=request.user)
        
        del form.fields['payment_method']
        del form.fields['requested_duration']
        if not is_admin(request.user):
            del form.fields['activation_dt']
            del form.fields['expiration_dt']
            del form.fields['list_type']
            del form.fields['entity']

        if form.is_valid():
            directory = form.save(commit=False)

            # update all permissions and save the model
            directory = update_perms_and_save(request, form, directory)

            # resize the image that has been uploaded
            try:
                logo = Image.open(directory.logo.path)
                logo.thumbnail((200,200),Image.ANTIALIAS)
                logo.save(directory.logo.path)
            except:
                pass

            log_defaults = {
                'event_id' : 442000,
                'event_data': '%s (%d) edited by %s' % (directory._meta.object_name, directory.pk, request.user),
                'description': '%s edited' % directory._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': directory,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % directory)
                                                                         
            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))             
        else:
            form = form_class(instance=directory, user=request.user)

        return render_to_response(template_name, {'directory': directory, 'form':form}, 
            context_instance=RequestContext(request))

    else:
        form = form_class(instance=directory, user=request.user)
        del form.fields['payment_method']
        del form.fields['requested_duration']
        if not is_admin(request.user):
            del form.fields['activation_dt']
            del form.fields['expiration_dt']
            del form.fields['list_type']
            del form.fields['entity']

    return render_to_response(template_name, {'directory': directory, 'form':form}, 
        context_instance=RequestContext(request))


@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="directories/edit-meta.html"):

    # check permission
    directory = get_object_or_404(Directory, pk=id)
    if not has_perm(request.user,'directories.change_directory',directory):
        raise Http403

    defaults = {
        'title': directory.get_title(),
        'description': directory.get_description(),
        'keywords': directory.get_keywords(),
        'canonical_url': directory.get_canonical_url(),
    }
    directory.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=directory.meta)
        if form.is_valid():
            directory.meta = form.save() # save meta
            directory.save() # save relationship
            
            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % directory)
             
            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))
    else:
        form = form_class(instance=directory.meta)

    return render_to_response(template_name, {'directory': directory, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=DirectoryForm, template_name="directories/add.html"):
    if not has_perm(request.user,'directories.add_directory'): raise Http403
    
    require_payment = get_setting('module', 'directories', 'directoriesrequirespayment')

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        del form.fields['expiration_dt']
        if not is_admin(request.user):
            del form.fields['activation_dt']
            del form.fields['entity']
        
        if not require_payment:
            del form.fields['payment_method']
            del form.fields['list_type']
            
        if form.is_valid():           
            directory = form.save(commit=False)

            # resize the image that has been uploaded
            try:
                logo = Image.open(directory.logo.path)
                logo.thumbnail((200,200),Image.ANTIALIAS)
                logo.save(directory.logo.path)
            except:
                pass
            
            if directory.payment_method: 
                directory.payment_method = directory.payment_method.lower()
            if not directory.requested_duration:
                directory.requested_duration = 30
            if not directory.list_type:
                directory.list_type = 'regular'
            directory.activation_dt = datetime.now()
            
            # set the expiration date
            directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)
            
            if not directory.status_detail: directory.status_detail = 'pending'

            # update all permissions and save the model
            directory = update_perms_and_save(request, form, directory)
            
            # create invoice
            directory_set_inv_payment(request.user, directory)

            log_defaults = {
                'event_id' : 441000,
                'event_data': '%s (%d) added by %s' % (directory._meta.object_name, directory.pk, request.user),
                'description': '%s added' % directory._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': directory,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % directory)
            
            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'directories', 'directoryrecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': directory,
                        'request': request,
                    }
                    notification.send_emails(recipients,'directory_added', extra_context)
                    
            if directory.payment_method.lower() in ['credit card', 'cc']:
                if directory.invoice and directory.invoice.balance > 0:
                    return HttpResponseRedirect(reverse('payments.views.pay_online', args=[directory.invoice.id, directory.invoice.guid])) 
                
            return HttpResponseRedirect(reverse('directory', args=[directory.slug]))
    else:
        form = form_class(user=request.user)
        
        del form.fields['expiration_dt']
        if not is_admin(request.user):
            del form.fields['activation_dt']
            del form.fields['entity']
        
        if not require_payment:
            del form.fields['payment_method']
            del form.fields['list_type']

    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))

    
@login_required
def delete(request, id, template_name="directories/delete.html"):
    directory = get_object_or_404(Directory, pk=id)

    if has_perm(request.user,'directories.delete_directory'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 443000,
                'event_data': '%s (%d) deleted by %s' % (directory._meta.object_name, directory.pk, request.user),
                'description': '%s deleted' % directory._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': directory,
            }
            
            EventLog.objects.log(**log_defaults)

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % directory)

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


@login_required
def pricing_add(request, form_class=DirectoryPricingForm, template_name="directories/pricing-add.html"):
    if has_perm(request.user,'directories.add_directorypricing'):
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():           
                directory_pricing = form.save(commit=False)
                directory_pricing.status = 1
                directory_pricing.save(request.user)
                
                log_defaults = {
                    'event_id' : 265100,
                    'event_data': '%s (%d) added by %s' % (directory_pricing._meta.object_name, directory_pricing.pk, request.user),
                    'description': '%s added' % directory_pricing._meta.object_name,
                    'user': request.user,
                    'request': request,
                    'instance': directory_pricing,
                }
                EventLog.objects.log(**log_defaults)
                
                return HttpResponseRedirect(reverse('directory_pricing.view', args=[directory_pricing.id]))
        else:
            form = form_class()
           
        return render_to_response(template_name, {'form':form}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def pricing_edit(request, id, form_class=DirectoryPricingForm, template_name="directories/pricing-edit.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, pk=id)
    if not has_perm(request.user,'directories.change_directorypricing',directory_pricing): Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=directory_pricing)
        if form.is_valid():           
            directory_pricing = form.save(commit=False)
            directory_pricing.save(request.user)
            
            log_defaults = {
                'event_id' : 265110,
                'event_data': '%s (%d) edited by %s' % (directory_pricing._meta.object_name, directory_pricing.pk, request.user),
                'description': '%s edited' % directory_pricing._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': directory_pricing,
            }
            EventLog.objects.log(**log_defaults)
            
            return HttpResponseRedirect(reverse('directory_pricing.view', args=[directory_pricing.id]))
    else:
        form = form_class(instance=directory_pricing)
       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))


@login_required
def pricing_view(request, id, template_name="directories/pricing-view.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, id=id)
    
    if has_perm(request.user,'directories.view_directorypricing',directory_pricing):        
        return render_to_response(template_name, {'directory_pricing': directory_pricing}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
    
@login_required
def pricing_delete(request, id, template_name="directories/pricing-delete.html"):
    directory_pricing = get_object_or_404(DirectoryPricing, pk=id)

    if not has_perm(request.user,'directories.delete_directorypricing'): raise Http403
       
    if request.method == "POST":
        log_defaults = {
            'event_id' : 265120,
            'event_data': '%s (%d) deleted by %s' % (directory_pricing._meta.object_name, directory_pricing.pk, request.user),
            'description': '%s deleted' % directory_pricing._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': directory_pricing,
        }
        
        EventLog.objects.log(**log_defaults)
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % directory_pricing)
        
        directory_pricing.delete()
            
        return HttpResponseRedirect(reverse('directory_pricing.search'))
    
    return render_to_response(template_name, {'directory_pricing': directory_pricing}, 
        context_instance=RequestContext(request))

def pricing_search(request, template_name="directories/pricing-search.html"):
    directory_pricing = DirectoryPricing.objects.all().order_by('duration')
    
    return render_to_response(template_name, {'directory_pricings':directory_pricing}, 
        context_instance=RequestContext(request))
    
