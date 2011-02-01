import uuid
from datetime import datetime


def legacy_user_is_admin(legacy_user):
    """
    Test if legacy user is an administrator in the legacy system
    """
    if legacy_user.securitylevel == 'administrator':
        return True
    return False

    
def legacy_user_is_developer(legacy_user):
    """
    Test if legacy user is a developer in the legacy system
    """
    if legacy_user.securitylevel == 'developer':
        return True
    return False


def get_profile_defaults(legacy_user):
    """
    Map the legacy user with the t4 profile model
    """
    profile_defaults = {
        'guid': str(uuid.uuid1()),
        'time_zone': 'US/Central',
        'language': 'en-us',
        'member_number': '',
        'historical_member_number': '',
        'salutation': legacy_user.salutation or '',
        'initials': legacy_user.initials or '',
        'display_name': legacy_user.displayname or '',
        'mailing_name': legacy_user.mailingname or '',
        'company': legacy_user.company or '',
        'position_title': legacy_user.positiontitle or '',
        'position_assignment': legacy_user.positionassignment or '',
        'sex': legacy_user.sex or '',
        'address': legacy_user.address or '',
        'address2': legacy_user.address2 or '',
        'city': legacy_user.city or '',
        'state': legacy_user.state or '',
        'zipcode': legacy_user.zipcode or '',
        'country': legacy_user.country or '',
        'county': legacy_user.county or '',
        'phone': legacy_user.phone or '',
        'phone2': legacy_user.phone2 or '',
        'fax': legacy_user.fax or '',
        'work_phone': legacy_user.workphone or '',
        'home_phone': legacy_user.homephone or '',
        'mobile_phone': legacy_user.mobilephone or '',
        'email': '',
        'email2': '',
        'url': legacy_user.url or '',
        'url2': legacy_user.url2 or '',
        'dob': legacy_user.dob or datetime.now(),
        'ssn': legacy_user.ssn or '',
        'spouse': legacy_user.spouse or '',
        'department': legacy_user.department or '',
        'education': legacy_user.education or '',
        'student': legacy_user.student or 0,
        'original_username': '',
        'remember_login': True,
        'exported': False,
        'direct_mail': False,
        'notes': '',
        'admin_notes': '',
        'referral_source': '',
        }
    
    return profile_defaults
    