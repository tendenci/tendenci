from django.template import Library


register = Library()


# Avatar and profile columns are always visible
# NOTE: Avatar col removed temporarily
PROFILE_DROPDOWN_MIN_COL_COUNT = 1
# Member column is always visible
COMMUNITY_DROPDOWN_MIN_COL_COUNT = 1
BOOTSTRAP_GRID_COL_COUNT = 12


@register.simple_tag(takes_context=True)
def get_profile_dropdown_column_size(context):
    col_count = PROFILE_DROPDOWN_MIN_COL_COUNT
    is_superuser = context['USER_IS_SUPERUSER']
    is_superuser_or_member = is_superuser or context['USER_IS_MEMBER']

    col_count += int(is_superuser_or_member) + int(is_superuser)

    return BOOTSTRAP_GRID_COL_COUNT / col_count


@register.simple_tag(takes_context=True)
def get_community_dropdown_column_size(context):
    col_count = COMMUNITY_DROPDOWN_MIN_COL_COUNT
    is_superuser = context['USER_IS_SUPERUSER']

    col_count += int(is_superuser)

    return BOOTSTRAP_GRID_COL_COUNT / col_count
