from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, TemplateDoesNotExist
from django.template import Template as DTemplate
from django.contrib import messages
from django.http import Http404, HttpResponse
from createsend import CreateSend
from createsend import Template as CST
from createsend.createsend import BadRequest
from perms.utils import has_perm
from campaign_monitor.models import Template
from campaign_monitor.forms import TemplateForm
from campaign_monitor.utils import temporary_id
from site_settings.utils import get_setting
from base.http import Http403

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

def template_index(request, template_name='campaign_monitor/templates/index.html'):
    if not has_perm(request.user, 'campaign_monitor.change_template'):
        raise Http403
    
    templates = Template.objects.all().order_by('id')
    
    return render_to_response(template_name, {'templates':templates}, 
        context_instance=RequestContext(request))

def template_view(request, template_id, template_name='campaign_monitor/templates/view.html'):
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403
        
    return render_to_response(template_name, {'template':template}, 
        context_instance=RequestContext(request))
        
def template_html(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)
    
    if not template.html_file:
        raise Http404
    
    text = DTemplate(template.html_file.file.read())
    context = RequestContext(request)
    
    response = HttpResponse(text.render(context))
    response['Content-Disposition'] = 'attachment; file=page.html'
    
    return response

def template_add(request, form_class=TemplateForm, template_name='campaign_monitor/templates/add.html'):
    
    if not has_perm(request.user,'campaign_monitor.add_template'):
        raise Http403
        
    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            #save template to generate urls
            template = form.save(commit=False)
            template.template_id = temporary_id()
            template.save()
            #set up urls
            site_url = get_setting('site', 'global', 'siteurl')
            html_url = "%s%s"%(site_url, template.get_html_url())
            if template.zip_file:
                zip_url = "%s%s"%(site_url, template.get_zip_url())
            else:
                zip_url = ""
            if template.screenshot_file:
                screenshot_url = "%s%s"%(site_url, template.get_screenshot_url())
            else:
                screenshot_url = ""
            
            #sync with campaign monitor
            try:
                t_id = CST().create(
                        client_id, template.name, 
                        html_url, zip_url, screenshot_url
                    )
            except BadRequest, e:
                messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
                template.delete()
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
            except Exception, e:
                messages.add_message(request, messages.ERROR, 'Error: %s' % e)
                template.delete()
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
            
            #get campaign monitor details
            t = CST(template_id=t_id).details()
            template.name = t.Name
            template.cm_preview_url = t.PreviewURL
            template.cm_screenshot_url = t.ScreenshotURL
            template.template_id = t_id
            template.save()
            
            messages.add_message(request, messages.INFO, 'Successfully created Template : %s' % t_id)
            
            return redirect(template)
                    
    else:
        form = form_class()
        
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
def template_edit(request, template_id, form_class=TemplateForm, template_name='campaign_monitor/templates/edit.html'):
    
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=template)
        if form.is_valid():
            
            #save template to generate urls
            template = form.save()
            
            #set up urls
            site_url = get_setting('site', 'global', 'siteurl')
            html_url = str("%s%s"%(site_url, template.get_html_url()))
            if template.zip_file:
                zip_url = str("%s%s"%(site_url, template.get_zip_url()))
            else:
                zip_url = ""
            if template.screenshot_file:
                screenshot_url = str("%s%s"%(site_url, template.get_screenshot_url()))
            else:
                screenshot_url = ""
            
            #sync with campaign monitor
            try:
                t = CST(template_id = form.instance.template_id)
                t.update(str(template.name), html_url, zip_url, screenshot_url)
            except BadRequest, e:
                messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
            except Exception, e:
                messages.add_message(request, messages.ERROR, 'Error: %s' % e)
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
                    
            #get campaign monitor details
            t = t.details()
            template.name = t.Name
            template.cm_preview_url = t.PreviewURL
            template.cm_screenshot_url = t.ScreenshotURL
            template.save()
                    
            messages.add_message(request, messages.INFO, 'Successfully updated Template : %s' % template.template_id)
            
            return redirect(template)
                    
    else:
        form = form_class(instance=template)
        
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
