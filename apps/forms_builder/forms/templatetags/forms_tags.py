from django.template import Node, Library, TemplateSyntaxError, Variable
from django.template.loader import get_template
from django.contrib.auth.models import AnonymousUser

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
    
    def __init__(self,  **kwargs):
        self.kwargs = kwargs

    def render(self, context):
        pk = 0

        if 'pk' in self.kwargs:
            try:
                pk = Variable(self.kwargs['pk'])
                pk = pk.resolve(context)
            except:
                pk = self.kwargs['pk'] # context string
                
        query = '"pk:%s"' % (pk)
        
        try:
            form = Form.objects.search(query=query).best_match()
            context['form'] = form.object
            context['form_for_form'] = FormForForm(form.object, AnonymousUser())
            template = get_template('forms/embed_form.html')
            output = '<div class="embed-form">%s</div>' % template.render(context)
            return output
        except:
            return ""        
        
@register.tag
def embed_form(parser, token):
    """
    Example:
        {% embed_form 123 %}
    """
    
    kwargs = {}
    bits = token.split_contents()
      
    try:
        kwargs["pk"] = bits[1]  
    except:
        message = "Form tag must include an ID of a form."
        raise TemplateSyntaxError(message)
    
    return GetFormNode(**kwargs) 