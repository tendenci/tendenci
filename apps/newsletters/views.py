import os.path
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from newsletters.forms import NewsletterAddForm
from user_groups.models import Group
from site_settings.utils import get_setting


def view_template(request, default=None, template_name=''):
    template_name_with_path = "newsletters/templates/"
    if default:
        template_name_with_path += "default/"
    template_name = template_name_with_path + template_name
    
    # test if we have this template, it not, raise http 404
    for dir in settings.TEMPLATE_DIRS:
        if os.path.isfile(os.path.join(dir, template_name)):
            return render_to_response(template_name, {}, 
                                      context_instance=RequestContext(request))
    raise Http404 
      

@login_required 
def add(request, form_class=NewsletterAddForm, template_name="newsletters/add.html"):
    if request.method == "POST":
        form = form_class(request.POST)
        
        if form.is_valid():
            pass
            #email = form.save(request.user)
            
            #return HttpResponseRedirect(reverse('email.view', args=[email.id]))
    else:
        from datetime import datetime
        now = datetime.now()
        now_str = now.strftime('%b %d, %Y')
        subject_initial = "%s Newsletter %s" % (get_setting('site', 'global', 'sitedisplayname'), now_str) 
        form = form_class(initial={'group':Group.objects.all(),
                                   'subject': subject_initial})

       
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))