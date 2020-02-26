# -*- coding: utf-8 -*-


import os
from django.db import migrations
from django.template.defaultfilters import slugify


def migrate_customized_jobs_templates():
    """
    Update those jobs templates that are pulled to sites

    jobs/add.html, jobs/edit.html:
    =============================

    Remove:
    <fieldset class="boxy-grey" >
     <legend id="category-title" style="cursor: pointer"><span>+</span> {% trans 'Category' %}</legend>
           <div id="category-form">
                  {{ categoryform|styled_form }}
              </div>
     </fieldset>

    Replace:
    <script type="text/javascript" src="{% static 'js/email-verification.js' %}"> </script>

    With:
    <script type="text/javascript" src="{% static 'js/email-verification.js' %}"> </script>
    <script type="text/javascript">{% include 'jobs/include/get_subcategories.js' %} </script>


    jobs/meta.html:
    ===============

    Replace:
    {% with job.category_set as job_cat %}

    With:
    {% with job.cat as job_cat %}

    Replace:
    {% if job_cat.category %}

    With:
    {% if job_cat %}

    Replace:
    categories={{ job_cat.category.pk }}">{{ job_cat.category }}

    With:
    cat={{ job_cat.pk }}">{{ job_cat.name }}

    Replace:
    {% if job_cat.sub_category %}

    With:
    {% if job.sub_cat %}


    Replace:
    subcategories={{ job_cat.sub_category.pk }}">{{ job_cat.sub_category }}

    With:
    cat={{ job_cat.pk }}&sub_cat={{ job.sub_cat.pk }}">{{ job.sub_cat.name }}


    Remove:
   <li>
        <a href="{% url 'category.update' job.opt_app_label job.opt_module_name job.pk %}">{% trans "Edit Categories" %}</a>
    </li>

    jobs/search-form.html:
    ======================

    Replace:
    form.categories

    With:
    form.cat

    Replace:
    form.subcategories

    With:
    form.sub_cat


    jobs/search.html:
    =================

    Replace:
    var $catAndSubcatSelect = $('#id_categories, #id_subcategories')

    With:
    var $catAndSubcatSelect = $('#id_cat, #id_sub_cat')


    jobs/top_nav_items.html:
    ========================

    Replace:
    <li class="content-item">
    <span class="app-name">
           <a href="{% url 'category.update' app_object.opt_app_label job.opt_module_name app_object.pk %}">{% trans "Edit Categories" %}</a>
     </span>
   </li>

   With:
   {% if request.user.is_superuser %}
        <li class="content-item">
            <span class="app-name">
                <a href="{% url 'admin:jobs_category_changelist' %}">{% trans "Manage Categories" %}</a>
            </span>
        </li>
    {% endif %}


    """
    import re
    from tendenci.apps.theme.utils import get_theme_root
    dir_path = get_theme_root()

    # jobs/add.html and edit.html
    files_list = ['{}/templates/jobs/add.html'.format(dir_path),
                  '{}/templates/jobs/edit.html'.format(dir_path)]
    for file_path in files_list:
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()

                # remove categoryform
                p = r'{0}([\d\D\s\S\w\W]*?){1}([\d\D\s\S\w\W]*?){2}'.format(re.escape('<fieldset class="boxy-grey" >'),
                                                                            re.escape('{{ categoryform|styled_form }}'),
                                                                            re.escape('</fieldset>'))
                content = re.sub(p, '', content)

                # add js link
                p = r'{0}\s*{1}'.format(re.escape('<script type="text/javascript" src="{% static \'js/email-verification.js\' %}">'),
                                        re.escape('</script>'))
                content = re.sub(p, '{0}\n{1}'.format('<script type="text/javascript" src="{% static \'js/email-verification.js\' %}"> </script>',
                                                      '<script type="text/javascript">{% include \'jobs/include/get_subcategories.js\' %} </script>)'),
                                 content)
            with open(file_path, 'w') as f:
                # save the updated content back to file
                f.write(content)

    # jobs/meta.html
    file_path = '{}/templates/jobs/meta.html'.format(dir_path)
    if os.path.isfile(file_path):
        find_replace_list = [('{% with job.category_set as job_cat %}', '{% with job.cat as job_cat %}'),
                             ('{% if job_cat.category %}', '{% if job_cat %}'),
                             ('categories={{ job_cat.category.pk }}">{{ job_cat.category }}', 'cat={{ job_cat.pk }}">{{ job_cat.name }}'),
                             ('{% if job_cat.sub_category %}', '{% if job.sub_cat %}'),
                             ('subcategories={{ job_cat.sub_category.pk }}">{{ job_cat.sub_category }}', 'cat={{ job_cat.pk }}&sub_cat={{ job.sub_cat.pk }}">{{ job.sub_cat.name }}'),
                             ]
        with open(file_path, 'r') as f:
            content = f.read()
            for (string_to_find, string_to_replace) in find_replace_list:
                content = content.replace(string_to_find, string_to_replace)

            p = r'{0}\s+{1}\s+{2}'.format(re.escape('<li>'),
                                        re.escape("""<a href="{% url 'category.update' job.opt_app_label job.opt_module_name job.pk %}">{% trans "Edit Categories" %}</a>"""),
                                        re.escape('</li>'))
            content = re.sub(p, '', content)

        with open(file_path, 'w') as f:
            f.write(content)

    # jobs/search-form.html
    file_path = '{}/templates/jobs/search-form.html'.format(dir_path)
    if os.path.isfile(file_path):
        find_replace_list = [('form.categories', 'form.cat'),
                             ('form.subcategories', 'form.sub_cat')
                             ]
        with open(file_path, 'r') as f:
            content = f.read()
            for (string_to_find, string_to_replace) in find_replace_list:
                content = content.replace(string_to_find, string_to_replace)

        with open(file_path, 'w') as f:
            f.write(content)

    # jobs/search.html
    file_path = '{}/templates/jobs/search.html'.format(dir_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            content = content.replace("var $catAndSubcatSelect = $('#id_categories, #id_subcategories')",
                                      "var $catAndSubcatSelect = $('#id_cat, #id_sub_cat')")
        with open(file_path, 'w') as f:
            f.write(content)

    #jobs/top_nav_items.html
    file_path = '{}/templates/jobs/top_nav_items.html'.format(dir_path)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            p = r'{0}\s+{1}\s+{2}\s+{3}\s+{4}'.format(
                                        re.escape('<li class="content-item">'),
                                        re.escape('<span class="app-name">'),
                                        re.escape("""<a href="{% url 'category.update' app_object.opt_app_label job.opt_module_name app_object.pk %}">{% trans "Edit Categories" %}</a>"""),
                                        re.escape('</span>'),
                                        re.escape('</li>'))
            manage_cat = """
            {% if request.user.is_superuser %}
            <li class="content-item">
                <span class="app-name">
                    <a href="{% url 'admin:jobs_category_changelist' %}">{% trans "Manage Categories" %}</a>
                </span>
            </li>
            {% endif %}
            """
            content = re.sub(p, manage_cat, content)

        with open(file_path, 'w') as f:
            f.write(content)


def migrate_categories_data(apps, schema_editor):
    from tendenci.apps.jobs.models import Job
    from tendenci.apps.jobs.models import Category as JobCategory
    #Job = apps.get_model("jobs", "Job")
    #JobCategory = apps.get_model("jobs", "Category")
    for job in Job.objects.all():
        job_cat, job_sub_cat = None, None
        cat_items = job.categories.all().order_by('category')
        for cat_item in cat_items:
            if cat_item.category:
                # category
                cat_name = cat_item.category.name
                if cat_name:
                    [job_cat] = JobCategory.objects.filter(name=cat_name,
                                                         parent__isnull=True)[:1] or [None]
                    if not job_cat:
                        job_cat = JobCategory(name=cat_name, slug=slugify(cat_name))
                        job_cat.save()
            elif cat_item.parent:
                # sub category
                sub_cat_name = cat_item.parent.name
                if sub_cat_name:
                    [job_sub_cat] = JobCategory.objects.filter(name=sub_cat_name,
                                                         parent=job_cat)[:1] or [None]
                    if not job_sub_cat:
                        job_sub_cat = JobCategory(name=sub_cat_name, slug=(sub_cat_name))
                        job_sub_cat.parent = job_cat
                        job_sub_cat.save()
        if job_cat:
            job.cat = job_cat
            if job_sub_cat:
                job.sub_cat = job_sub_cat
            job.save(log=False)

    migrate_customized_jobs_templates()


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20170910_1701'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_data),
    ]
