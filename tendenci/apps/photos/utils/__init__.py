

def get_privacy_settings(instance):
    """
    Returns a dictionary of all Tendenci
    privacy settings
    """
    return {
        'allow_anonymous_view': instance.allow_anonymous_view,
        'allow_user_view': instance.allow_user_view,
        'allow_member_view': instance.allow_member_view,
        'allow_user_edit': instance.allow_user_edit,
        'allow_member_edit': instance.allow_member_edit,
        'status': instance.status,
        'status_detail': instance.status_detail
    }
