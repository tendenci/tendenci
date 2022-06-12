from django.template import Library, Node, Variable
from django.apps import apps
from django import template

from tendenci.apps.categories.models import Category

register = Library()

class GetCategoryForObjectNode(Node):
    def __init__(self, object, context):
        self.object = Variable(object)
        self.context = context
    def render(self, context):
        if not self.context: self.context = 'category'
        if not self.object:
            context[self.context] = ''
            return ''
        object = self.object.resolve(context)
        category = Category.objects.get_for_object(object, 'category')
        if category: context[self.context] = category
        else: context[self.context] = ''
        return ''

@register.tag
def get_category_for_object(parser, token):
    """
        {% get_category_for_object object %}
    """
    bits  = token.split_contents()

    try: object = bits[1]
    except: object = None

    try: context = bits[3]
    except: context = None

    return GetCategoryForObjectNode(object, context)


class GetCategoriesForModelNode(Node):
    def __init__(self, name, context):
        self.name = name
        self.context = context

    def render(self, context):
        if not self.context:
            self.context = 'categories'
        if not self.name:
            context[self.context] = ''
            return ''

        model = apps.get_model(self.name)
        if not model:
            context[self.context] = ''
            return ''
        categories = Category.objects.get_for_model(model)[0]
        if categories:
            context[self.context] = categories
        else:
            context[self.context] = ''
        return ''


@register.tag
def get_categories_for_model(parser, token):
    """
        {% get_categories_for_model "articles.Article" as articles_categories %}
    """
    bits  = token.split_contents()

    try:
        name = bits[1]
    except:
        name = None

    try:
        context = bits[3]
    except:
        context = None
        
    if not (name[0] == name[-1] and name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % bits[0])

    return GetCategoriesForModelNode(name[1:-1], context)


class GetSubCategoryForObjectNode(Node):
    def __init__(self, object, context):
        self.object = Variable(object)
        self.context = context
    def render(self, context):
        if not self.context: self.context = 'sub_category'
        if not self.object:
            context[self.context] = ''
            return ''
        object = self.object.resolve(context)
        category = Category.objects.get_for_object(object, 'sub_category')
        if category: context[self.context] = category
        else: context[self.context] = ''
        return ''


@register.tag
def get_sub_category_for_object(parser, token):
    """
        {% get_sub_category_for_object object as sub_category %}
    """
    bits  = token.split_contents()

    try: object = bits[1]
    except: object = None

    try: context = bits[3]
    except: context = None

    return GetSubCategoryForObjectNode(object, context)
