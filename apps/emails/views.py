from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from emails.forms import EmailForm
from emails.models import Email
from site_settings.utils import get_setting
from base.http import Http403
from perms.utils import is_admin, has_perm

@login_required 
def add(request, form_class=EmailForm, template_name="emails/edit.html"):
    if request.method == "POST":
        form = form_class(request.POST)
        
        if form.is_valid():
            email = form.save(request.user)
            
            return HttpResponseRedirect(reverse('email.view', args=[email.id]))
    else:
        form = form_class(initial={'sender':request.user.email, 
                                   'sender_display': request.user.get_full_name,
                                   'reply_to': request.user.email})

       
    return render_to_response(template_name, {'form':form, 'email':None}, 
        context_instance=RequestContext(request))
    
    
def view(request, id, template_name="emails/view.html"):
    email = get_object_or_404(Email, pk=id)
    
    if not email.allow_view_by(request.user): raise Http403
       
    return render_to_response(template_name, {'email':email}, 
        context_instance=RequestContext(request))
    
@login_required 
def edit(request, id, form_class=EmailForm, template_name="emails/edit.html"):
    email = get_object_or_404(Email, pk=id)
    if not email.allow_edit_by(request.user): raise Http403
    
    next = request.REQUEST.get("next", "")
    if request.method == "POST":
        form = form_class(request.POST, instance=email)
        
        if form.is_valid():
            email = form.save(request.user)
            
            if not next or ' ' in next:
                next = reverse('email.view', args=[email.id])
            
            return HttpResponseRedirect(next)
    else:
        form = form_class(instance=email)

       
    return render_to_response(template_name, {'form':form, 'email':email, 'next':next}, 
        context_instance=RequestContext(request))
    
def search(request, template_name="emails/search.html"):
    if is_admin(request.user):
        emails = Email.objects.all()
    else:
        emails = Email.objects.filter(status=True, status_detail='active')
    emails = emails.order_by('-create_dt')
    
    return render_to_response(template_name, {'emails':emails}, 
        context_instance=RequestContext(request))
    
def delete(request, id, template_name="emails/delete.html"):
    email = get_object_or_404(Email, pk=id)
    
    if not has_perm(request.user,'emails.delete_email',email): raise Http403

    if request.method == "POST":
        email.delete()
        return HttpResponseRedirect(reverse('email.search'))

    return render_to_response(template_name, {'email':email}, 
        context_instance=RequestContext(request))
    
