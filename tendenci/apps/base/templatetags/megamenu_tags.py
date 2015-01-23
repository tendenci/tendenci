from django.template import Library


register = Library()


PROFILE_DROPDOWN_MIN_COL_COUNT = 1                      # Avatar and profile columns are always visible
                                                        # NOTE: Avatar col removed temporarily
COMMUNITY_DROPDOWN_MIN_COL_COUNT = 1                    # Member column is always visible
BOOTSTRAP_GRID_COL_COUNT = 12


@register.assignment_tag(takes_context=True)
def get_profile_dropdown_column_size(context):
    col_count = PROFILE_DROPDOWN_MIN_COL_COUNT
    is_superuser = context['USER_IS_SUPERUSER']
    is_superuser_or_member = is_superuser or context['USER_IS_MEMBER']
    
    col_count += int(is_superuser_or_member) + int(is_superuser)

    return BOOTSTRAP_GRID_COL_COUNT / col_count


@register.assignment_tag(takes_context=True)
def get_community_dropdown_column_size(context):
    col_count = COMMUNITY_DROPDOWN_MIN_COL_COUNT
    is_superuser = context['USER_IS_SUPERUSER']

    col_count += int(is_superuser)

    return BOOTSTRAP_GRID_COL_COUNT / col_count
