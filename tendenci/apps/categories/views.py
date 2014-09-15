from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from tendenci.core.base.http import Http403
from tendenci.core.categories.forms import CategoryForm
from tendenci.core.categories.models import Category

@login_required
def edit_categories(request, app_label, model, pk, form_class=CategoryForm, template_name="categories/update.html"):
    # get the content type
    try: content_type = ContentType.objects.get(app_label=app_label,model=model)
    except: raise Http404

    # get the object
    try: object = content_type.get_object_for_this_type(pk=pk)
    except: raise Http404

    # check permissions
    perm_tuple = (object._meta.app_label, object._meta.module_name)
    if not request.user.has_perm('%s.change_%s' % perm_tuple, object):
        raise Http403

    category = Category.objects.get_for_object(object,'category')
    sub_category = Category.objects.get_for_object(object,'sub_category')

    initial_form_data = {
        'app_label': app_label,
        'model': model,
        'pk': pk,
        'category': getattr(category,'name','0'),
        'sub_category': getattr(sub_category,'name','0')
    }

    if request.method == 'POST':
        form = form_class(content_type, request.POST)
        if form.is_valid():
            # update the category of the article
            category_removed = False
            category = form.cleaned_data['category']
            if category != '0':
                Category.objects.update(object,category,'category')
            else: # remove
                category_removed = True
                Category.objects.remove(object,'category')
                Category.objects.remove(object,'sub_category')

            if not category_removed:
                # update the sub category of the article
                sub_category = form.cleaned_data['sub_category']
                if sub_category != '0':
                    Category.objects.update(object,sub_category,'sub_category')
                else: # remove
                    Category.objects.remove(object,'sub_category')

            # kind of a bummer, but save the object to update the search index.
            # TODO: find a better way to update the index if a category has been changed
            object.save()

            messages.add_message(request, messages.SUCCESS, _('Successfully updated %(m)s categories.' % {'m':model}))
            return HttpResponseRedirect(reverse('category.update',
                                         args=[form.cleaned_data['app_label'],
                                               form.cleaned_data['model'],
                                               form.cleaned_data['pk']]))
        else:
            form = form_class(content_type, request.POST, initial=initial_form_data)
    else:
        form = form_class(content_type, initial=initial_form_data)

    if not request.user.profile.is_superuser:
        # remove the add links for non-admins
        form.fields['category'].help_text = ''
        form.fields['sub_category'].help_text = ''

    response_data = {
        'object':object,
        'form':form,
        'app_label': app_label,
        'model': model,
    }

    return render_to_response(template_name, response_data,
            context_instance=RequestContext(request))

