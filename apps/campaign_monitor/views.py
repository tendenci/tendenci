from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, TemplateDoesNotExist
from django.template import Template as DTemplate
from django.contrib import messages
from django.http import Http404, HttpResponse
from createsend import CreateSend
from createsend import Template as CST
from createsend import Campaign as CSC
from createsend.createsend import BadRequest
from perms.utils import has_perm
from campaign_monitor.models import Template, Campaign
from campaign_monitor.forms import TemplateForm, CampaignForm
from campaign_monitor.utils import temporary_id, extract_files
from campaign_monitor.utils import sync_campaigns, sync_templates
from campaign_monitor.utils import apply_template_media
from site_settings.utils import get_setting
from base.http import Http403

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

@login_required
def template_index(request, template_name='campaign_monitor/templates/index.html'):
    if not has_perm(request.user, 'campaign_monitor.view_template'):
        raise Http403
    
    templates = Template.objects.all().order_by('name')
    
    return render_to_response(template_name, {'templates':templates}, 
        context_instance=RequestContext(request))

@login_required
def template_view(request, template_id, template_name='campaign_monitor/templates/view.html'):
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.view_template', template):
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
    
def template_render(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)
    
    if not template.html_file:
        raise Http404
    
    text = DTemplate(apply_template_media(template))
    context = RequestContext(request)
    
    response = HttpResponse(text.render(context))
    
    return response
    
def template_text(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)
    
    # return dummy data temporarily
    return HttpResponse("Lorem Ipsum")

@login_required
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
            
            #sync with campaign monitor
            try:
                t_id = CST().create(
                        client_id, template.name, 
                        html_url, zip_url
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
            template.template_id = t_id
            template.name = t.Name
            template.cm_preview_url = t.PreviewURL
            template.cm_screenshot_url = t.ScreenshotURL
            template.save()
            
            #extract and serve files in zip
            extract_files(template)
            
            messages.add_message(request, messages.INFO, 'Successfully created Template : %s' % t_id)
            
            return redirect(template)
                    
    else:
        form = form_class()
        
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
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
            
            #sync with campaign monitor
            try:
                t = CST(template_id = form.instance.template_id)
                t.update(str(template.name), html_url, zip_url)
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
            
            #extract and serve files in zip
            extract_files(template)
                    
            messages.add_message(request, messages.INFO, 'Successfully updated Template : %s' % template.template_id)
            
            return redirect(template)
                    
    else:
        form = form_class(instance=template)
        
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def template_update(request, template_id):
    """
    This method makes use of the same files to update the CM Template.
    Useful for updating data/content only and retaining design.
    """
    
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.change_template', template):
        raise Http403
    
    #set up urls
    site_url = get_setting('site', 'global', 'siteurl')
    html_url = str("%s%s"%(site_url, template.get_html_url()))
    if template.zip_file:
        zip_url = str("%s%s"%(site_url, template.get_zip_url()))
    else:
        zip_url = ""
    
    #sync with campaign monitor
    try:
        t = CST(template_id = template.template_id)
        t.update(str(template.name), html_url, zip_url)
    except BadRequest, e:
        messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
        return redirect(template)
    except Exception, e:
        messages.add_message(request, messages.ERROR, 'Error: %s' % e)
        return redirect(template)
            
    #get campaign monitor details
    t = t.details()
    template.name = t.Name
    template.cm_preview_url = t.PreviewURL
    template.cm_screenshot_url = t.ScreenshotURL
    template.save()
    
    messages.add_message(request, messages.INFO, 'Successfully updated Template : %s' % template.template_id)
    
    return redirect(template)
    
@login_required
def template_delete(request, template_id):
    template = get_object_or_404(Template, template_id=template_id)
    
    if not has_perm(request.user,'campaign_monitor.delete_template', template):
        raise Http403
    
    t_id = template.template_id
    
    try:
        CST(template_id=t_id).delete()
    except BadRequest, e:
        messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
        return redirect(template)
    except Exception, e:
        messages.add_message(request, messages.ERROR, 'Error: %s' % e)
        return redirect(template)
    
    template.delete()
    messages.add_message(request, messages.INFO, 'Successfully deleted Template : %s' % t_id)
    
    return redirect("campaign_monitor.template_index")
    
@login_required
def template_sync(request):
    if not has_perm(request.user,'campaign_monitor.add_template'):
        raise Http403
    
    sync_templates()
    
    messages.add_message(request, messages.INFO, 'Successfully synced with Campaign Monitor')
    return redirect("campaign_monitor.template_index")

@login_required
def campaign_index(request, template_name='campaign_monitor/campaigns/index.html'):
    if not has_perm(request.user, 'campaign_monitor.view_campaigns'):
        raise Http403
    
    campaigns = Campaign.objects.all().order_by('name')
    
    return render_to_response(template_name, {'campaigns':campaigns}, 
        context_instance=RequestContext(request))

@login_required
def campaign_view(request, campaign_id, template_name='campaign_monitor/campaigns/view.html'):
    campaign = get_object_or_404(Campaign, campaign_id=campaign_id)
    
    if not has_perm(request.user,'campaign_monitor.view_campaign', campaign):
        raise Http403
    
    return render_to_response(template_name, {'campaign':campaign}, 
        context_instance=RequestContext(request))

@login_required
def campaign_sync(request):
    if not has_perm(request.user,'campaign_monitor.add_campaign'):
        raise Http403
    
    sync_campaigns()
    
    messages.add_message(request, messages.INFO, 'Successfully synced with Campaign Monitor')
    return redirect("campaign_monitor.campaign_index")

#@login_required
#def campaign_add(request, form_class=CampaignForm, template_name='campaign_monitor/campaigns/add.html'):
#    
#    if not has_perm(request.user,'campaign_monitor.add_campaign'):
#        raise Http403
#        
#    if request.method == "POST":
#        form = form_class(request.POST)
#        if form.is_valid():
#            campaign = form.save(commit=False)
#            
#            #prepare data
#            list_ids = [list.list_id for list in form.cleaned_data['lists']]
#            site_url = get_setting('site', 'global', 'siteurl')
#            html_url = "%s%s" % (site_url, campaign.template.get_render_url())
#            text_url = "%s%s" % (site_url, campaign.template.get_text_url())
#            
#            try:
#                c_id = CSC().create(
#                    client_id, campaign.subject, campaign.name, 
#                    campaign.from_name, campaign.from_email,
#                    campaign.reply_to, html_url, text_url, 
#                    list_ids, []
#                )
#            except BadRequest, e:
#                messages.add_message(request, messages.ERROR, 'Bad Request %s: %s' % (e.data.Code, e.data.Message))
#                return render_to_response(template_name, {'form':form}, 
#                context_instance=RequestContext(request))
#            except Exception, e:
#                messages.add_message(request, messages.ERROR, 'Error: %s' % e)
#                return render_to_response(template_name, {'form':form}, 
#                    context_instance=RequestContext(request))
#            
#            campaign.campaign_id = c_id
#            campaign.save()
#            messages.add_message(request, messages.INFO, 'Successfully created Campaign: %s' % c_id)
#            return redirect(campaign)
#    else:
#        copy_id = request.GET.get('copy', None)
#        
#        if copy_id:
#            #get campaign to be copied
#            copy = get_object_or_404(Campaign, campaign_id=campaign_id)
#            copy_data = {
#                "name": copy.name,
#                "subject": copy.subject,
#                "from_name": copy.from_name,
#                "from_email": copy.from_email,
#                "reply_to": copy.reply_to,
#                "template": copy.template,
#                "lists": copy.lists
#            }
#            form = form_class(initial=copy_data)
#        else:
#            form = form_class()
#        
#    return render_to_response(template_name, {'form':form}, 
#        context_instance=RequestContext(request))

@login_required
def campaign_generate(request, form_class=CampaignForm, template_name='campaign_monitor/campaigns/add.html'):
    if not has_perm(request.user,'campaign_monitor.add_campaign'):
        raise Http403
        
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            return redirect("%s/createsend/step1.aspx" % settings.CAMPAIGNMONITOR_URL)
    else:
        form = form_class()
        
    return render_to_response(template_name,
        {'form':form},
        context_instance=RequestContext(request))
