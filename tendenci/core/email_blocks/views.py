from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from tendenci.core.email_blocks.forms import EmailBlockForm
from tendenci.core.email_blocks.models import EmailBlock
#from tendenci.core.site_settings.utils import get_setting
from tendenci.core.base.http import Http403
from tendenci.core.perms.utils import has_perm

@login_required
def add(request, form_class=EmailBlockForm, template_name="email_blocks/edit.html"):
    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid():
            email_block = form.save(request.user)

            return HttpResponseRedirect(reverse('email_block.view', args=[email_block.id]))
    else:
        form = form_class()


    return render_to_response(template_name, {'form':form, 'email_block':None},
        context_instance=RequestContext(request))

@login_required
def view(request, id, template_name="email_blocks/view.html"):
    email_block = get_object_or_404(EmailBlock, pk=id)

    if not email_block.allow_view_by(request.user): raise Http403

    return render_to_response(template_name, {'email_block':email_block},
        context_instance=RequestContext(request))

@login_required
def edit(request, id, form_class=EmailBlockForm, template_name="email_blocks/edit.html"):
    email_block = get_object_or_404(EmailBlock, pk=id)

    if not email_block.allow_edit_by(request.user): raise Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=email_block)

        if form.is_valid():
            email_block = form.save(request.user)

            return HttpResponseRedirect(reverse('email_block.view', args=[email_block.id]))
    else:
        form = form_class(instance=email_block)


    return render_to_response(template_name, {'form':form, 'email_block':email_block},
        context_instance=RequestContext(request))

@login_required
def search(request, template_name="email_blocks/search.html"):
    if request.user.profile.is_superuser:
        email_blocks = EmailBlock.objects.all()
    else:
        raise Http403
    email_blocks = email_blocks.order_by('-create_dt')

    return render_to_response(template_name, {'email_blocks':email_blocks},
        context_instance=RequestContext(request))

@login_required
def delete(request, id, template_name="email_blocks/delete.html"):
    email_block = get_object_or_404(EmailBlock, pk=id)

    if not has_perm(request.user,'email_blocks.delete_email_block',email_block): raise Http403

    if request.method == "POST":
        email_block.delete()
        return HttpResponseRedirect(reverse('email_block.search'))

    return render_to_response(template_name, {'email_block':email_block},
        context_instance=RequestContext(request))

