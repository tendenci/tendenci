from django import template

register = template.Library()


@register.filter
def filter_by_featured(projects):
    featured_projects = []
    for project in projects:
        if project.featured:
            featured_projects.append(project)
    return featured_projects


@register.filter
def filter_by_category(projects, category_id):
    cat_projects = []
    for project in projects:
        if category_id in project.category.all().values_list('id', flat=True):
            cat_projects.append(project)
    return cat_projects


@register.filter
def filter_by_other(projects):
    """
    Return projects that are not featured and no categories.
    """
    other_projects = []
    for project in projects:
        if not project.featured and not project.category.exists():
            other_projects.append(project)
    return other_projects

