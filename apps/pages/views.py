import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

from base.http import Http403
from base.utils import check_template
from event_logs.models import EventLog
from meta.models import Meta as MetaTags
from meta.forms import MetaForm
from perms.utils import (update_perms_and_save, get_notice_recipients,
    is_admin, has_perm,  get_query_filters)
from categories.forms import CategoryForm
from categories.models import Category
from site_settings.utils import get_setting
from theme.shortcuts import themed_response as render_to_response
from files.models import file_directory

from pages.models import Page, HeaderImage
from pages.forms import PageForm

try:
    from notification import models as notification
except:
    notification = None

def index(request, slug=None, template_name="pages/view.html"):
    if not slug: return HttpResponseRedirect(reverse('page.search'))
    page = get_object_or_404(Page, slug=slug)
    
    # non-admin can not view the non-active content
    # status=0 has been taken care of in the has_perm function
    if (page.status_detail).lower() <> 'active' and (not is_admin(request.user)):
        raise Http403

    if not page.template or not check_template(page.template):
        page.template = "pages/base.html"

    if has_perm(request.user,'pages.view_page',page):
        log_defaults = {
            'event_id' : 585000,
            'event_data': '%s (%d) viewed by %s' % (page._meta.object_name, page.pk, request.user),
            'description': '%s viewed' % page._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': page,
        }
        EventLog.objects.log(**log_defaults)        
        
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

def search(request, template_name="pages/search.html"):
    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        pages = Page.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'pages.view_page')
        pages = Page.objects.filter(filters).distinct()
        if request.user.is_authenticated():
            pages = pages.select_related() 
    pages = pages.order_by('-create_dt')

    log_defaults = {
        'event_id' : 584000,
        'event_data': '%s searched by %s' % ('Page', request.user),
        'description': '%s searched' % 'Page',
        'user': request.user,
        'request': request,
        'source': 'pages'
    }
    EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name, {'pages':pages}, 
        context_instance=RequestContext(request))

def print_view(request, slug, template_name="pages/print-view.html"):
    
    page = get_object_or_404(Page, slug=slug)

    if has_perm(request.user,'pages.view_page',page):
        log_defaults = {
            'event_id' : 585001,
            'event_data': '%s (%d) viewed by %s' % (page._meta.object_name, page.pk, request.user),
            'description': '%s viewed - print view' % page._meta.object_name,
            'user': request.user,
            'request': request,
            'instance': page,
        }
        EventLog.objects.log(**log_defaults)
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def edit(request, id, form_class=PageForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="pages/edit.html"):
        
    page = get_object_or_404(Page, pk=id)
    
    if not has_perm(request.user,'pages.change_page',page):
        raise Http403
    
    content_type = get_object_or_404(ContentType, app_label='pages',model='page')
    
    #setup categories
    category = Category.objects.get_for_object(page,'category')
    sub_category = Category.objects.get_for_object(page,'sub_category')
        
    initial_category_form_data = {
        'app_label': 'pages',
        'model': 'page',
        'pk': page.pk,
        'category': getattr(category,'name','0'),
        'sub_category': getattr(sub_category,'name','0')
    }

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=page, user=request.user)
        metaform = meta_form_class(request.POST, instance=page.meta, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, initial= initial_category_form_data, prefix='category')
        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            page = form.save(commit=False)
            # update all permissions and save the model
            page = update_perms_and_save(request, form, page)
            
            # handle header image
            f = form.cleaned_data['header']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get(app_label="pages", model="headerimage")
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                header.file.save(filename, f)
                page.header_image = header
            
            #save meta
            meta = metaform.save()
            page.meta = meta
            
            ## update the category of the article
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0': 
                Category.objects.update(page ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(page ,'category')
                Category.objects.remove(page ,'sub_category')
            
            if not category_removed:
                # update the sub category of the article
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0': 
                    Category.objects.update(page, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(page,'sub_category')
                    
            #save relationships
            page.save()
            
            log_defaults = {
                'event_id' : 582000,
                'event_data': '%s (%d) edited by %s' % (page._meta.object_name, page.pk, request.user),
                'description': '%s edited' % page._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': page,
            }
            EventLog.objects.log(**log_defaults)               

            messages.add_message(request, messages.SUCCESS, 'Successfully updated %s' % page)
            
            if not is_admin(request.user):
                # send notification to administrators
                recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': page,
                            'request': request,
                        }
                        notification.send_emails(recipients,'page_edited', extra_context)
                                                          
            return HttpResponseRedirect(reverse('page', args=[page.slug]))             
    else:
        form = form_class(instance=page, user=request.user)
        metaform = meta_form_class(instance=page.meta, prefix='meta')
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')
    
    return render_to_response(template_name,
        {
            'page': page, 
            'form':form, 
            'metaform':metaform,
            'categoryform':categoryform,
        },
        context_instance=RequestContext(request))

@login_required
def edit_meta(request, id, form_class=MetaForm, template_name="pages/edit-meta.html"):

    # check permission
    page = get_object_or_404(Page, pk=id)
    if not has_perm(request.user,'pages.change_page',page):
        raise Http403

    defaults = {
        'title': page.get_title(),
        'description': page.get_description(),
        'keywords': page.get_keywords(),
        'canonical_url': page.get_canonical_url(),
    }
    page.meta = MetaTags(**defaults)

    if request.method == "POST":
        form = form_class(request.POST, instance=page.meta)
        if form.is_valid():
            page.meta = form.save() # save meta
            page.save() # save relationship

            messages.add_message(request, messages.SUCCESS, 'Successfully updated meta for %s' % page)
            
            return HttpResponseRedirect(reverse('page', args=[page.slug]))
    else:
        form = form_class(instance=page.meta)

    return render_to_response(template_name, {'page': page, 'form':form}, 
        context_instance=RequestContext(request))

@login_required
def add(request, form_class=PageForm, meta_form_class=MetaForm, category_form_class=CategoryForm, template_name="pages/add.html"):
    
    if not has_perm(request.user,'pages.add_page'):
        raise Http403
    
    content_type = get_object_or_404(ContentType, app_label='pages',model='page')
    
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=request.user)
        metaform = meta_form_class(request.POST, prefix='meta')
        categoryform = category_form_class(content_type, request.POST, prefix='category')
        if form.is_valid() and metaform.is_valid() and categoryform.is_valid():
            page = form.save(commit=False)
            
            # add all permissions and save the model
            page = update_perms_and_save(request, form, page)
            
            # handle header image
            f = form.cleaned_data['header']
            if f:
                header = HeaderImage()
                header.content_type = ContentType.objects.get(app_label="pages", model="headerimage")
                header.creator = request.user
                header.creator_username = request.user.username
                header.owner = request.user
                header.owner_username = request.user.username
                filename = "%s-%s" % (page.slug, f.name)
                header.file.save(filename, f)
                page.header_image = header
            
            #save meta
            meta = metaform.save()
            page.meta = meta
            
            #setup categories
            category = Category.objects.get_for_object(page,'category')
            sub_category = Category.objects.get_for_object(page,'sub_category')
            
            ## update the category of the article
            category_removed = False
            category = categoryform.cleaned_data['category']
            if category != '0': 
                Category.objects.update(page ,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(page ,'category')
                Category.objects.remove(page ,'sub_category')
            
            if not category_removed:
                # update the sub category of the article
                sub_category = categoryform.cleaned_data['sub_category']
                if sub_category != '0': 
                    Category.objects.update(page, sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(page,'sub_category')  
            
            #save relationships
            page.save()

            log_defaults = {
                'event_id' : 581000,
                'event_data': '%s (%d) added by %s' % (page._meta.object_name, page.pk, request.user),
                'description': '%s added' % page._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': page,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully added %s' % page)
            
            if not is_admin(request.user):
                # send notification to administrators
                recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'object': page,
                            'request': request,
                        }
                        notification.send_emails(recipients,'page_added', extra_context)
                
            return HttpResponseRedirect(reverse('page', args=[page.slug]))
    else:
        initial_category_form_data = {
            'app_label': 'pages',
            'model': 'page',
            'pk': 0, #not used for this view but is required for the form
        }
        form = form_class(user=request.user)
        metaform = meta_form_class(prefix='meta')
        categoryform = category_form_class(content_type, initial=initial_category_form_data, prefix='category')
    return render_to_response(template_name, 
            {
                'form':form,
                'metaform':metaform,
                'categoryform':categoryform,
            },
            context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="pages/delete.html"):
    page = get_object_or_404(Page, pk=id)

    if has_perm(request.user,'pages.delete_page'):   
        if request.method == "POST":
            log_defaults = {
                'event_id' : 583000,
                'event_data': '%s (%d) deleted by %s' % (page._meta.object_name, page.pk, request.user),
                'description': '%s deleted' % page._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': page,
            }
            EventLog.objects.log(**log_defaults)
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted %s' % page)
            
            # send notification to administrators
            recipients = get_notice_recipients('module', 'pages', 'pagerecipients')
            if recipients:
                if notification:
                    extra_context = {
                        'object': page,
                        'request': request,
                    }
                    notification.send_emails(recipients,'page_deleted', extra_context)
            
            page.delete()
            return HttpResponseRedirect(reverse('page.search'))
    
        return render_to_response(template_name, {'page': page}, 
            context_instance=RequestContext(request))
    else:
        raise Http403
