from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from createsend import CreateSend
from createsend import Template as CST
from perms.utils import has_perm
from campaign_monitor.models import Template
from campaign_monitor.forms import TemplateForm

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

def template_index(request, template_name='campaign_monitor/templates/index.html'):
    if not has_perm(request.user, 'campaign_monitor.change_template'):
        raise Http403
    
    templates = Template.objects.all()
        
    return render_to_response(template_name, {'templates':templates}, 
        context_instance=RequestContext(request))

def template_view(request, template_id, template_name='campaign_monitor/templates/view.html'):
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403
        
    return render_to_response(template_name, {'template':template}, 
        context_instance=RequestContext(request))

def template_add(request, form_class=TemplateForm, template_name='campaign_monitor/templates/add.html'):
    
    if not has_perm(request.user,'campaign_monitor.add_template'):
        raise Http403
        
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            #save template to generate urls
            template = form.save()
            
            #sync with campaign monitor
            try:
                t = CST.create(
                        client_id, template.name, template.html_url(),
                        template.zip_url(), template.screenshot_url()
                    )
            except BadRequest, e:
                messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
                template.delete() #delete failed entry
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
            except Exception, e:
                messages.add_message(request, messages.ERROR, 'Error: %s' % e)
                template.delete() #delete failed entry
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
                    
            messages.add_message(request, messages.INFO, 'Successfully created Template : %s' % t.TemplateID)
            template.template_id = t.TemplateID
            template.save()
            
            return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
                    
    else:
        form = form_class()
        
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
def template_edit(request, template_id, form_class=TemplateForm, template_name='campaign_monitor/templates/edit.html'):
    
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403
        
    if request.method == "POST":
        form = form_class(request.POST, instance=template)
        if form.is_valid():
            #save template to generate urls
            template = form.save()
            
            #sync with campaign monitor
            try:
                t = CST(template_id = self.instance.template_id)
                t.update(name, html, zip, screenshot)
            except BadRequest, e:
                messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
            except Exception, e:
                messages.add_message(request, messages.ERROR, 'Error: %s' % e)
                return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
                    
            messages.add_message(request, messages.INFO, 'Successfully updated Template : %s' % t.TemplateID)
            
            return render_to_response(template_name, {'form':form}, 
                    context_instance=RequestContext(request))
                    
    else:
        form = form_class(instance=template)
        
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
