from django.template import Library
from django.contrib.auth.models import AnonymousUser
from django.utils.safestring import mark_safe

from tendenci.apps.forms_builder.forms.forms import FormForForm
from tendenci.apps.forms_builder.forms.models import Form

register = Library()


@register.inclusion_tag("forms/options.html", takes_context=True)
def forms_options(context, user, form):
    context.update({
        "opt_object": form,
        "user": user
    })
    return context


@register.inclusion_tag("forms/nav.html", takes_context=True)
def forms_nav(context, user, form=None):
    context.update({
        "nav_object": form,
        "user": user
    })
    return context


@register.inclusion_tag("forms/search-form.html", takes_context=True)
def forms_search(context):
    return context


@register.inclusion_tag("forms/top_nav_items.html", takes_context=True)
def form_current_app(context, user, form=None):
    app_object = form
    # ensure this form is a form object
    if not form or not hasattr(form, 'pk'):
        app_object = None
    context.update({
        "app_object": app_object,
        "user": user
    })
    return context


@register.inclusion_tag("forms/entry_options.html", takes_context=True)
def forms_entry_options(context, user, entry):
    context.update({
        "opt_object": entry,
        "user": user
    })
    return context


# class GetFormNode(Node):
#
#     def __init__(self, **kwargs):
#         self.kwargs = kwargs
#
#     def render(self, context):
#         pk = 0
#         template_name = 'forms/embed_form_new.html'
#
#         if 'pk' in self.kwargs:
#             try:
#                 pk = Variable(self.kwargs['pk'])
#                 pk = pk.resolve(context)
#             except:
#                 pk = self.kwargs['pk']  # context string
#
#         if 'template_name' in self.kwargs:
#             try:
#                 template_name = Variable(self.kwargs['template_name'])
#                 template_name = pk.resolve(context)
#             except:
#                 template_name = self.kwargs['template_name']  # context string
#
#             template_name = template_name.replace('"', '')
#
#         try:
#             form = Form.objects.get(pk=pk)
#             context['embed_form'] = form.object
#             context['embed_form_for_form'] = FormForForm(form.object, AnonymousUser())
#             template = context.template.engine.get_template(template_name)
#             output = '<div class="embed-form">%s</div>' % template.render(context=context)
#             return output
#         except:
#             try:
#                 form = Form.objects.get(pk=pk)
#                 context['embed_form'] = form
#                 context['embed_form_for_form'] = FormForForm(form, AnonymousUser())
#                 template = context.template.engine.get_template(template_name)
#                 output = '<div class="embed-form">%s</div>' % template.render(context=context)
#                 return output
#             except:
#                 raise
#                 return ""


@register.simple_tag(takes_context=True)
def embed_form(context, pk, *args, **kwargs):
    """
    Example:
        {% embed_form 123 [template] [gsize='compact'] %}
    """
    if len(args) > 0:
        template_name = args[0]
    else:
        template_name = 'forms/embed_form_new.html'

    [form] = Form.objects.filter(pk=pk)[:1] or [None]
    if not form:
        return ""

    if hasattr(form, 'object'):
        form_obj = form.object
    else:
        form_obj = form

    try:
        context['embed_form'] = form_obj
        context['embed_form_for_form'] = FormForForm(form_obj, AnonymousUser())
        if 'captcha' in context['embed_form_for_form'].fields and 'gsize' in kwargs:
            if hasattr(context['embed_form_for_form'].fields['captcha'].widget, 'gtag_attrs'):
                context['embed_form_for_form'].fields['captcha'].widget.gtag_attrs.update(
                                {'data-size': kwargs['gsize']})
        template = context.template.engine.get_template(template_name)
        output = '<div class="embed-form">%s</div>' % template.render(context=context)
        return mark_safe(output)
    except:
        return ""


@register.filter
def media_url(field):
    """
    example: field|media_url
    """
    # from django.conf import settings
    from django.urls import reverse

    # internal url; we handle privacy
    return reverse('form_files', args=[field.pk])
