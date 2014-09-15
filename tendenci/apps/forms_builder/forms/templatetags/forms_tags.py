from django.template import Node, Library, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_lazy as _

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


@register.inclusion_tag("forms/entry_options.html", takes_context=True)
def forms_entry_options(context, user, entry):
    context.update({
        "opt_object": entry,
        "user": user
    })
    return context


class GetFormNode(Node):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def render(self, context):
        pk = 0
        template_name = 'forms/embed_form.html'

        if 'pk' in self.kwargs:
            try:
                pk = Variable(self.kwargs['pk'])
                pk = pk.resolve(context)
            except:
                pk = self.kwargs['pk']  # context string

        if 'template_name' in self.kwargs:
            try:
                template_name = Variable(self.kwargs['template_name'])
                template_name = pk.resolve(context)
            except:
                template_name = self.kwargs['template_name']  # context string

            template_name = template_name.replace('"', '')

        try:
            form = Form.objects.get(pk=pk)
            context['form'] = form.object
            context['form_for_form'] = FormForForm(form.object, AnonymousUser())
            template = get_template(template_name)
            output = '<div class="embed-form">%s</div>' % template.render(context)
            return output
        except:
            try:
                form = Form.objects.get(pk=pk)
                context['form'] = form
                context['form_for_form'] = FormForForm(form, AnonymousUser())
                template = get_template(template_name)
                output = '<div class="embed-form">%s</div>' % template.render(context)
                return output
            except:
                return ""


@register.tag
def embed_form(parser, token):
    """
    Example:
        {% embed_form 123 [template] %}
    """

    kwargs = {}
    bits = token.split_contents()

    try:
        kwargs["pk"] = bits[1]
    except:
        message = "Form tag must include an ID of a form."
        raise TemplateSyntaxError(_(message))
    try:
        kwargs["template_name"] = bits[2]
    except:
        pass
    return GetFormNode(**kwargs)


@register.filter
def media_url(field):
    """
    example: field|media_url
    """
    # from django.conf import settings
    from django.core.urlresolvers import reverse

    # internal url; we handle privacy
    return reverse('form_files', args=[field.pk])
