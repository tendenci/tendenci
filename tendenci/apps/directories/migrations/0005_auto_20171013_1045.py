# -*- coding: utf-8 -*-
import os

from django.db import migrations
from django.template.defaultfilters import slugify


def migrate_customized_directories_templates():
    """
    Update those directories templates that are pulled to sites

    directories/add.html, directories/edit.html:
    ============================================

    Replace:
    <script type="text/javascript" src="{% static 'js/email-verification.js' %}"> </script>

    With:
    <script type="text/javascript" src="{% static 'js/email-verification.js' %}"> </script>
    <script type="text/javascript">{% include 'directories/include/get_subcategories.js' %} </script>


    directories/meta.html:
    ======================

    Replace:
    {% with directory.category_set as directory_cat %}

    With:
    {% with directory.cat as directory_cat %}

    Replace:
    {% if directory_cat.category %}

    With:
    {% if directory_cat %}

    Replace:
    category={{ directory_cat.category.pk }}">{{ directory_cat.category }}

    With:
    cat={{ directory_cat.pk }}">{{ directory_cat.name }}

    Replace:
    {% if directory_cat.sub_category %}

    With:
    {% if directory.sub_cat %}


    Replace:
    sub_category={{ directory_cat.sub_category.pk }}">{{ directory_cat.sub_category }}

    With:
    cat={{ directory_cat.pk }}&sub_cat={{ directory.sub_cat.pk }}">{{ directory.sub_cat.name }}


    Remove:
   <li>
        <a href="{% url 'category.update' directory.opt_app_label directory.opt_module_name directory.pk %}">{% trans "Edit Categories" %}</a>
    </li>

    directories/search-form.html:
    ======================

    # Remove:
    {% for form.category in form.category_list %}
        {{ form.category.name }}
    {% endfor %}


    Replace:
    form.category

    With:
    form.cat

    Replace:
    form.sub_category

    With:
    form.sub_cat


    directories/search.html:
    =================

    Replace:
    var $catAndSubcatSelect = $('#id_category, #id_sub_category')

    With:
    var $catAndSubcatSelect = $('#id_cat, #id_sub_cat')


    directories/top_nav_items.html:
    ========================

    Replace:
    <li class="content-item">
      <span class="app-name">
        <a href="{% url 'category.update' app_object.opt_app_label app_object.opt_module_name app_object.pk %}">{% trans "Edit Categories" %}</a>
       </span>
    </li>

   With:
   {% if request.user.is_superuser %}
        <li class="content-item">
            <span class="app-name">
                <a href="{% url 'admin:directories_category_changelist' %}">{% trans "Manage Categories" %}</a>
            </span>
        </li>
    {% endif %}


    """
    import re
    from tendenci.apps.theme.utils import get_theme_root
    dir_path = get_theme_root()

    # directories/add.html and edit.html
    files_list = ['{}/templates/directories/add.html'.format(dir_path),
                  '{}/templates/directories/edit.html'.format(dir_path)]
    for file_path in files_list:
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()

                # add js link
                p = r'{0}\s*{1}'.format(re.escape('<script type="text/javascript" src="{% static \'js/email-verification.js\' %}">'),
                                        re.escape('</script>'))
                content = re.sub(p, '{0}\n{1}'.format('<script type="text/javascript" src="{% static \'js/email-verification.js\' %}"> </script>',
                                                      '<script type="text/javascript">\n{% include \'directories/include/get_subcategories.js\' %} \n</script>'),
                                 content)
            with open(file_path, 'w') as f:
                # save the updated content back to file
                f.write(content)

    # directories/meta.html
    file_path = '{}/templates/directories/meta.html'.format(dir_path)
    if os.path.isfile(file_path):
        find_replace_list = [('{% with directory.category_set as directory_cat %}', '{% with directory.cat as directory_cat %}'),
                             ('{% if directory_cat.category %}', '{% if directory_cat %}'),
                             ('category={{ directory_cat.category.id }}">{{ directory_cat.category }}', 'cat={{ directory_cat.pk }}">{{ directory_cat.name }}'),
                             ('{% if directory_cat.sub_category %}', '{% if directory.sub_cat %}'),
                             ('sub_category={{ directory_cat.sub_category.id }}">{{ directory_cat.sub_category }}', 'cat={{ directory_cat.pk }}&sub_cat={{ directory.sub_cat.pk }}">{{ directory.sub_cat.name }}'),
                             ]
        with open(file_path, 'r') as f:
            content = f.read()
            for (string_to_find, string_to_replace) in find_replace_list:
                content = content.replace(string_to_find, string_to_replace)

            p = r'{0}\s+{1}\s+{2}'.format(re.escape('<li>'),
                                        re.escape("""<a href="{% url 'category.update' directory.opt_app_label directory.opt_module_name directory.pk %}">{% trans "Edit Categories" %}</a>"""),
                                        re.escape('</li>'))
            content = re.sub(p, '', content)

        with open(file_path, 'w') as f:
            f.write(content)

    # directories/search-form.html
    file_path = '{}/templates/directories/search-form.html'.format(dir_path)
    if os.path.isfile(file_path):
        find_replace_list = [('form.category', 'form.cat'),
                             ('form.sub_category', 'form.sub_cat')
                             ]
        with open(file_path, 'r') as f:
            content = f.read()

            # remove
            p = r'{0}\s*{1}\s*{2}'.format(re.escape('{% for form.category in form.category_list %}'),
                                                re.escape(' {{ form.category.name }}'),
                                                re.escape('{% endfor %}'))
            content = re.sub(p, '', content)

            for (string_to_find, string_to_replace) in find_replace_list:
                content = content.replace(string_to_find, string_to_replace)

        with open(file_path, 'w') as f:
            f.write(content)

    # directories/search.html
    file_path = '{}/templates/directories/search.html'.format(dir_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            content = content.replace("var $catAndSubcatSelect = $('#id_category, #id_sub_category')",
                                      "var $catAndSubcatSelect = $('#id_cat, #id_sub_cat')")
        with open(file_path, 'w') as f:
            f.write(content)

    #directories/top_nav_items.html
    file_path = '{}/templates/directories/top_nav_items.html'.format(dir_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            p = r'{0}\s+{1}\s+{2}\s+{3}\s+{4}'.format(
                                        re.escape('<li class="content-item">'),
                                        re.escape('<span class="app-name">'),
                                        re.escape("""<a href="{% url 'category.update' app_object.opt_app_label app_object.opt_module_name app_object.pk %}">{% trans "Edit Categories" %}</a>"""),
                                        re.escape('</span>'),
                                        re.escape('</li>'))
            manage_cat = """
            {% if request.user.is_superuser %}
            <li class="content-item">
                <span class="app-name">
                    <a href="{% url 'admin:directories_category_changelist' %}">{% trans "Manage Categories" %}</a>
                </span>
            </li>
            {% endif %}
            """
            content = re.sub(p, manage_cat, content)

        with open(file_path, 'w') as f:
            f.write(content)

def migrate_categories_data(apps, schema_editor):
    from tendenci.apps.directories.models import Directory
    from tendenci.apps.directories.models import Category as DirectoryCategory

    for directory in Directory.objects.raw('SELECT * FROM directories_directory'):
        directory_cat, directory_sub_cat = None, None
        cat_items = directory.categories.all().order_by('category')
        for cat_item in cat_items:
            if cat_item.category:
                # category
                cat_name = cat_item.category.name
                if cat_name:
                    [directory_cat] = DirectoryCategory.objects.filter(name=cat_name,
                                                         parent__isnull=True)[:1] or [None]
                    if not directory_cat:
                        directory_cat = DirectoryCategory(name=cat_name, slug=slugify(cat_name))
                        directory_cat.save()
            elif cat_item.parent:
                # sub category
                sub_cat_name = cat_item.parent.name
                if sub_cat_name:
                    [directory_sub_cat] = DirectoryCategory.objects.filter(name=sub_cat_name,
                                                         parent=directory_cat)[:1] or [None]
                    if not directory_sub_cat:
                        directory_sub_cat = DirectoryCategory(name=sub_cat_name, slug=(sub_cat_name))
                        directory_sub_cat.parent = directory_cat
                        directory_sub_cat.save()
        if directory_cat:
            directory.cat = directory_cat
            if directory_sub_cat:
                directory.sub_cat = directory_sub_cat
            directory.save(log=False)

    migrate_customized_directories_templates()

class Migration(migrations.Migration):

    dependencies = [
        ('directories', '0004_auto_20171013_1043'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_data),
    ]
