from django.template import Node, Library, TemplateSyntaxError, Variable
from django.template.loader import get_template

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form

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
        "nav_object" : form,
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
    
    def __init__(self, pk):
        self.pk = pk

    def render(self, context):
        query = '"pk:%s"' % (self.pk)
        print query
        
        form = Form.objects.search(query=query).best_match()
        context['form'] = form.object
        context['form_for_form'] = FormForForm(form.object)
        template = get_template('forms/embed_form.html')
        output = '<div class="embed_form">%s</div>' % template.render(context)
        return output
        
        
@register.tag
def embed_form(parser, token):
    """
    Example:
        {% embed_form 123 %}
    """
    bits = token.split_contents()
    
    try:
        pk = bits[1]  
    except:
        message = "Form tag must include an ID of a form."
        raise TemplateSyntaxError(message)
    
    return GetFormNode(pk) 