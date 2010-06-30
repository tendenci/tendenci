import os
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from newsletters.forms import NewsletterAddForm
#from user_groups.models import Group
from site_settings.utils import get_setting


def view_template(request, template_name='', template_path='newsletters/templates/'):
    template_name = template_path + template_name
    
    # test if we have this template, it not, raise http 404
    for dir in settings.TEMPLATE_DIRS:
        if os.path.isfile(os.path.join(dir, template_name)):
            return render_to_response(template_name, {}, 
                                      context_instance=RequestContext(request))
    raise Http404 
      

@login_required 
def add(request, form_class=NewsletterAddForm, template_name="newsletters/add.html"):
    template_selected = ''
    if request.method == "POST":
        form = form_class(request.POST)
        template_selected = request.POST.get('template', '')
        
        if form.is_valid():
            form.save(request)
           
            #email = form.save(request.user)
            
            #return HttpResponseRedirect(reverse('email.view', args=[email.id]))
    else:
        import datetime
        now = datetime.datetime.now()
        now_str = now.strftime('%b %d, %Y')
        subject_initial = "%s Newsletter %s" % (get_setting('site', 'global', 'sitedisplayname'), now_str)
        # 3 months from now but on the first day of the month
        event_end_dt =  now + datetime.timedelta(days=90)
        event_end_dt = datetime.date(event_end_dt.year, event_end_dt.month, 1)
        form = form_class(initial={
                                   'subject': subject_initial,
                                   'event_start_dt': now,
                                   'event_end_dt': event_end_dt})
        
    # the default templates and site specific templates need to be displayed in the 
    # separate blocks, thus we have to render them separately in the template.
    # get a list of default templates
    default_templates = []
    default_dir = os.path.join(os.path.join(settings.PROJECT_ROOT, "templates"), 'newsletters/templates/default')
    
    if os.path.isdir(default_dir):
        default_templates = os.listdir(default_dir)
        default_templates = ['default/'+ t for t in default_templates]
        
    # get a list of site specific templates
    templates = []
    for dir in settings.TEMPLATE_DIRS:
        dir = os.path.join(dir, 'newsletters/templates')
        if os.path.isdir(dir):
            template_names = os.listdir(dir)
            for template in template_names:
                if os.path.isfile(os.path.join(dir, template)):
                    templates.append(template)
    
    return render_to_response(template_name, {'form':form, 
                                              'default_templates': default_templates,
                                              'templates': templates,
                                              'template_selected': template_selected}, 
        context_instance=RequestContext(request))