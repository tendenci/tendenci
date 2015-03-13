from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.categories.models import Category, CategoryItem


class CategoryField(forms.ChoiceField):
    """
    A ``ChoiceField`` which validates that its input is a valid category string
    """
    def clean(self, value):
        value = super(CategoryField, self).clean(value)
        return value

category_defaults = {
    'label':_('Category'),
    'choices': [],
    'help_text': format_html(u'{0}{1}{2}',
        mark_safe('''
            <span id="t-categories-add-category-help-text" class="help-block">
                <button type="button" class="btn btn-link" data-toggle="modal" data-target="#t-categories-add-category-modal">
        '''),
        _(u'Add Category'),
        mark_safe('''
                </button>
            </span>
        ''')
    )
}

sub_category_defaults = {
    'label':_('Subcategory'),
    'choices': [],
    'help_text': format_html(u'{0}{1}{2}',
        mark_safe('''
            <span id="t-categories-add-subcategory-help-text" class="help-block">
                <button type="button" class="btn btn-link" data-toggle="modal" data-target="#t-categories-add-subcategory-modal">
        '''),
        _(u'Add Subcategory'),
        mark_safe('''
                </button>
            </span>
        ''')
    )
}


class CategoryForm(FormControlWidgetMixin, forms.Form):
    category = CategoryField(**category_defaults)
    sub_category = CategoryField(**sub_category_defaults)

    # instance fields needed to generate content types
    app_label = forms.CharField(widget=forms.HiddenInput())
    model = forms.CharField(widget=forms.HiddenInput())
    pk = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, content_type, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        if args:
            post_data = args[0]
        else:
            post_data = None

        prefix = kwargs.get('prefix', None)

        # set up the category (no parent) choices
        distinct_cat_ids = CategoryItem.objects.filter(content_type_id=content_type.id
                                                       ).filter(parent__id__isnull=True
                                                    ).values_list('category_id', flat=True
                                                                  ).distinct()
        categories = Category.objects.filter(id__in=distinct_cat_ids
                                             ).values_list('name', flat=True
                                                           ).order_by('name')

        categories = [[cat, cat] for cat in categories]
        categories.insert(0,[0,'------------'])
        if post_data:
            if prefix:
                new_category = post_data.get('%s-category'%prefix,'0')
            else:
                new_category = post_data.get('category','0')
            if new_category != '0':
                categories.append([new_category,new_category])
        self.fields['category'].choices = tuple(categories)

        # set up the sub category choices
        distinct_cat_ids = CategoryItem.objects.filter(content_type_id=content_type.id
                                                       ).filter(category__id__isnull=True
                                                    ).values_list('parent_id', flat=True
                                                                  ).distinct()
        sub_categories = Category.objects.filter(id__in=distinct_cat_ids
                                             ).values_list('name', flat=True
                                                           ).order_by('name')

        sub_categories = [[cat, cat] for cat in sub_categories]
        sub_categories.insert(0,[0,'------------'])
        if post_data:
            if prefix:
                new_sub_category = post_data.get('%s-sub_category'%prefix,'0')
            else:
                new_sub_category = post_data.get('sub_category','0')
            if new_sub_category != '0':
                sub_categories.append([new_sub_category,new_sub_category])
        self.fields['sub_category'].choices = tuple(sub_categories)


class CategoryForm2(CategoryForm):
    """
        CategoryForm with no Add Category and Add Subcategory links.
    """
    category = CategoryField(label=_('Category'), choices = [])
    sub_category = CategoryField(label=_('Sub Category'), choices = [])
