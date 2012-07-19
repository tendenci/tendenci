import datetime
import cPickle
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from actions.forms import ActionSLAForm, ActionStep5Form
from actions.models import Action
from site_settings.utils import get_setting
from base.http import Http403
from perms.utils import has_perm

# in order to send email instantly, the number of members in group should be less than LIMIT
# no longer needed cause we're queueing the emails on amazon
#LIMIT = 50

@login_required 
def view(request, action_id, template_name="actions/view.html"):
    action = get_object_or_404(Action, pk=action_id)
    if not has_perm(request.user,'actions.add_action'): raise Http403
    
    return render_to_response(template_name, {'action':action}, 
        context_instance=RequestContext(request))
    
    
@login_required 
def step4(request, action_id, form_class=ActionSLAForm, template_name="actions/step4.html"):
    action = get_object_or_404(Action, pk=action_id)
    if not has_perm(request.user,'actions.add_action'): raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST, instance=action)
        
        if form.is_valid():
            form.save()
            
            return HttpResponseRedirect(reverse('action.step5', args=[action.id]))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'form':form, 'action':action}, 
        context_instance=RequestContext(request))
    
@login_required 
def step5(request, action_id, form_class=ActionStep5Form, template_name="actions/step5.html"):
    action = get_object_or_404(Action, pk=action_id)
    if not has_perm(request.user,'actions.add_action'): raise Http403
    
    if request.method == "POST":
        form = form_class(request.POST)
        
        if form.is_valid():
            add_article = form.cleaned_data['add_article']
            if add_article:
                # add an article
                from articles.models import Article
                from categories.models import Category
                from perms.object_perms import ObjectPermission
                from django.template.defaultfilters import slugify
                
                # article slug is a unique field, if the slug already exists,
                # what should we do? let append the action id to it to keep it unique
                slug = slugify(action.email.subject + '-' + str(action.id))
                try:
                    art = Article.objects.get(slug=slug)
                except Article.DoesNotExist:
                    art = Article()
                    art.headline = action.email.subject
                    art.slug = slug
                    art.summary = ""
                    art.body = action.email.body
                    art.sourct = request.user.get_full_name()
                    art.first_name = request.user.first_name
                    art.last_name = request.user.last_name
                    profile = request.user.get_profile()
                    art.phone = profile.phone
                    art.fax = profile.fax
                    art.email = profile.email
                    art.website = get_setting('site', 'global', 'siteurl')
                    art.release_dt = datetime.datetime.now()
                    
                    if action.member_only:
                        art.allow_anonymous_view = 1
                        art.allow_user_view = 1
                    art.allow_member_view = 1
                    art.allow_anonymous_edit = 0
                    art.allow_user_edit = 0
                    art.allow_member_edit = 0
                    art.status = 1
                    art.status_detail = 'active'
                    
                    art.creator = request.user
                    art.creator_username = request.user.username
                    art.owner = request.user
                    art.owner_username = request.user.username
                    art.save()
                
                    # user group - assign the permission to view this article
                    if action.group:
                        ObjectPermission.objects.assign_group(action.group, art)
                    
                    # update category
                    category = Category.objects.update(art, 'Newsletter', 'category')
                
                action.article = art
                
                action.save()
                
            #if action.group.members.count() < LIMIT:
            return HttpResponseRedirect(reverse('action.send', args=[action.id]))
            #else:
            #    # return to confirmation page    
            #    return HttpResponseRedirect(reverse('action.confirm', args=[action.id]))
    else:
        form = form_class()
    
    return render_to_response(template_name, {'form':form, 'action':action}, 
        context_instance=RequestContext(request))
    
@login_required 
def confirm(request, action_id, template_name="actions/confirm.html"):
    action = get_object_or_404(Action, pk=action_id)
    if not has_perm(request.user,'actions.add_action'): raise Http403
    
    if action.status_detail == 'open':
        action.status_detail = 'submitted'
        action.submit_dt = datetime.datetime.now()
        action.sla = True
        action.save()
        
    return render_to_response(template_name, {'action':action}, 
        context_instance=RequestContext(request))
    
@login_required 
def send(request, action_id):
    action = get_object_or_404(Action, pk=action_id)
    if not has_perm(request.user,'actions.add_action'): raise Http403
    
    if action.status_detail == 'open':
        from actions.utils import distribute_newsletter_v2
        boo = distribute_newsletter_v2(action)
        
#        if action.group.members.count() < LIMIT:
#            # send the newsletter immediately
#            from actions.utils import distribute_newsletter_v2
#            boo = distribute_newsletter_v2(action)
#        else:
#            from actions.tasks import task_queue_distribute_newsletter
#            result = task_queue_distribute_newsletter.delay(action)
#            # store the AsyncResult of the task so we can check the state of the task later
#            action.task_result = cPickle.dumps(result)
#            action.save()
    
    return HttpResponseRedirect(reverse('action.confirm', args=[action.id]))

@login_required 
def recap(request, action_id, template_name="actions/recap.html"):
    action = get_object_or_404(Action, pk=action_id)
    
    if not has_perm(request.user,'actions.add_action'): raise Http403
    
    import cPickle
    action_recaps = action.actionrecap_set.all()
    for action_recap in action_recaps:
        action_recap.recap = cPickle.loads(action_recap.recap.encode('utf-8'))
    
    return render_to_response(template_name, {'action':action, 'action_recaps': action_recaps}, 
        context_instance=RequestContext(request))