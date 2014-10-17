from django.core.cache import cache
from django.conf import settings as d_settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.site_settings.models import Setting
from tendenci.core.site_settings.cache import SETTING_PRE_KEY

COUNTRIES = (
    ('', '-----------'),
    ('AD', _('Andorra')),
    ('AE', _('United Arab Emirates')),
    ('AF', _('Afghanistan')),
    ('AG', _('Antigua & Barbuda')),
    ('AI', _('Anguilla')),
    ('AL', _('Albania')),
    ('AM', _('Armenia')),
    ('AN', _('Netherlands Antilles')),
    ('AO', _('Angola')),
    ('AQ', _('Antarctica')),
    ('AR', _('Argentina')),
    ('AS', _('American Samoa')),
    ('AT', _('Austria')),
    ('AU', _('Australia')),
    ('AW', _('Aruba')),
    ('AZ', _('Azerbaijan')),
    ('BA', _('Bosnia and Herzegovina')),
    ('BB', _('Barbados')),
    ('BD', _('Bangladesh')),
    ('BE', _('Belgium')),
    ('BF', _('Burkina Faso')),
    ('BG', _('Bulgaria')),
    ('BH', _('Bahrain')),
    ('BI', _('Burundi')),
    ('BJ', _('Benin')),
    ('BM', _('Bermuda')),
    ('BN', _('Brunei Darussalam')),
    ('BO', _('Bolivia')),
    ('BR', _('Brazil')),
    ('BS', _('Bahama')),
    ('BT', _('Bhutan')),
    ('BV', _('Bouvet Island')),
    ('BW', _('Botswana')),
    ('BY', _('Belarus')),
    ('BZ', _('Belize')),
    ('CA', _('Canada')),
    ('CC', _('Cocos (Keeling) Islands')),
    ('CF', _('Central African Republic')),
    ('CG', _('Congo')),
    ('CH', _('Switzerland')),
    ('CI', _('Ivory Coast')),
    ('CK', _('Cook Iislands')),
    ('CL', _('Chile')),
    ('CM', _('Cameroon')),
    ('CN', _('China')),
    ('CO', _('Colombia')),
    ('CR', _('Costa Rica')),
    ('CU', _('Cuba')),
    ('CV', _('Cape Verde')),
    ('CX', _('Christmas Island')),
    ('CY', _('Cyprus')),
    ('CZ', _('Czech Republic')),
    ('DE', _('Germany')),
    ('DJ', _('Djibouti')),
    ('DK', _('Denmark')),
    ('DM', _('Dominica')),
    ('DO', _('Dominican Republic')),
    ('DZ', _('Algeria')),
    ('EC', _('Ecuador')),
    ('EE', _('Estonia')),
    ('EG', _('Egypt')),
    ('EH', _('Western Sahara')),
    ('ER', _('Eritrea')),
    ('ES', _('Spain')),
    ('ET', _('Ethiopia')),
    ('FI', _('Finland')),
    ('FJ', _('Fiji')),
    ('FK', _('Falkland Islands (Malvinas)')),
    ('FM', _('Micronesia')),
    ('FO', _('Faroe Islands')),
    ('FR', _('France')),
    ('FX', _('France, Metropolitan')),
    ('GA', _('Gabon')),
    ('GB', _('United Kingdom (Great Britain)')),
    ('GD', _('Grenada')),
    ('GE', _('Georgia')),
    ('GF', _('French Guiana')),
    ('GH', _('Ghana')),
    ('GI', _('Gibraltar')),
    ('GL', _('Greenland')),
    ('GM', _('Gambia')),
    ('GN', _('Guinea')),
    ('GP', _('Guadeloupe')),
    ('GQ', _('Equatorial Guinea')),
    ('GR', _('Greece')),
    ('GS', _('South Georgia and the South Sandwich Islands')),
    ('GT', _('Guatemala')),
    ('GU', _('Guam')),
    ('GW', _('Guinea-Bissau')),
    ('GY', _('Guyana')),
    ('HK', _('Hong Kong')),
    ('HM', _('Heard & McDonald Islands')),
    ('HN', _('Honduras')),
    ('HR', _('Croatia')),
    ('HT', _('Haiti')),
    ('HU', _('Hungary')),
    ('ID', _('Indonesia')),
    ('IE', _('Ireland')),
    ('IL', _('Israel')),
    ('IN', _('India')),
    ('IO', _('British Indian Ocean Territory')),
    ('IQ', _('Iraq')),
    ('IR', _('Islamic Republic of Iran')),
    ('IS', _('Iceland')),
    ('IT', _('Italy')),
    ('JM', _('Jamaica')),
    ('JO', _('Jordan')),
    ('JP', _('Japan')),
    ('KE', _('Kenya')),
    ('KG', _('Kyrgyzstan')),
    ('KH', _('Cambodia')),
    ('KI', _('Kiribati')),
    ('KM', _('Comoros')),
    ('KN', _('St. Kitts and Nevis')),
    ('KP', _('Korea, Democratic People\'s Republic of')),
    ('KR', _('Korea, Republic of')),
    ('KW', _('Kuwait')),
    ('KY', _('Cayman Islands')),
    ('KZ', _('Kazakhstan')),
    ('LA', _('Lao People\'s Democratic Republic')),
    ('LB', _('Lebanon')),
    ('LC', _('Saint Lucia')),
    ('LI', _('Liechtenstein')),
    ('LK', _('Sri Lanka')),
    ('LR', _('Liberia')),
    ('LS', _('Lesotho')),
    ('LT', _('Lithuania')),
    ('LU', _('Luxembourg')),
    ('LV', _('Latvia')),
    ('LY', _('Libyan Arab Jamahiriya')),
    ('MA', _('Morocco')),
    ('MC', _('Monaco')),
    ('MD', _('Moldova, Republic of')),
    ('MG', _('Madagascar')),
    ('MH', _('Marshall Islands')),
    ('ML', _('Mali')),
    ('MN', _('Mongolia')),
    ('MM', _('Myanmar')),
    ('MO', _('Macau')),
    ('MP', _('Northern Mariana Islands')),
    ('MQ', _('Martinique')),
    ('MR', _('Mauritania')),
    ('MS', _('Monserrat')),
    ('MT', _('Malta')),
    ('MU', _('Mauritius')),
    ('MV', _('Maldives')),
    ('MW', _('Malawi')),
    ('MX', _('Mexico')),
    ('MY', _('Malaysia')),
    ('MZ', _('Mozambique')),
    ('NA', _('Namibia')),
    ('NC', _('New Caledonia')),
    ('NE', _('Niger')),
    ('NF', _('Norfolk Island')),
    ('NG', _('Nigeria')),
    ('NI', _('Nicaragua')),
    ('NL', _('Netherlands')),
    ('NO', _('Norway')),
    ('NP', _('Nepal')),
    ('NR', _('Nauru')),
    ('NU', _('Niue')),
    ('NZ', _('New Zealand')),
    ('OM', _('Oman')),
    ('PA', _('Panama')),
    ('PE', _('Peru')),
    ('PF', _('French Polynesia')),
    ('PG', _('Papua New Guinea')),
    ('PH', _('Philippines')),
    ('PK', _('Pakistan')),
    ('PL', _('Poland')),
    ('PM', _('St. Pierre & Miquelon')),
    ('PN', _('Pitcairn')),
    ('PR', _('Puerto Rico')),
    ('PT', _('Portugal')),
    ('PW', _('Palau')),
    ('PY', _('Paraguay')),
    ('QA', _('Qatar')),
    ('RE', _('Reunion')),
    ('RO', _('Romania')),
    ('RU', _('Russian Federation')),
    ('RW', _('Rwanda')),
    ('SA', _('Saudi Arabia')),
    ('SB', _('Solomon Islands')),
    ('SC', _('Seychelles')),
    ('SD', _('Sudan')),
    ('SE', _('Sweden')),
    ('SG', _('Singapore')),
    ('SH', _('St. Helena')),
    ('SI', _('Slovenia')),
    ('SJ', _('Svalbard & Jan Mayen Islands')),
    ('SK', _('Slovakia')),
    ('SL', _('Sierra Leone')),
    ('SM', _('San Marino')),
    ('SN', _('Senegal')),
    ('SO', _('Somalia')),
    ('SR', _('Suriname')),
    ('ST', _('Sao Tome & Principe')),
    ('SV', _('El Salvador')),
    ('SY', _('Syrian Arab Republic')),
    ('SZ', _('Swaziland')),
    ('TC', _('Turks & Caicos Islands')),
    ('TD', _('Chad')),
    ('TF', _('French Southern Territories')),
    ('TG', _('Togo')),
    ('TH', _('Thailand')),
    ('TJ', _('Tajikistan')),
    ('TK', _('Tokelau')),
    ('TM', _('Turkmenistan')),
    ('TN', _('Tunisia')),
    ('TO', _('Tonga')),
    ('TP', _('East Timor')),
    ('TR', _('Turkey')),
    ('TT', _('Trinidad & Tobago')),
    ('TV', _('Tuvalu')),
    ('TW', _('Taiwan, Province of China')),
    ('TZ', _('Tanzania, United Republic of')),
    ('UA', _('Ukraine')),
    ('UG', _('Uganda')),
    ('UM', _('United States Minor Outlying Islands')),
    ('US', _('United States of America')),
    ('UY', _('Uruguay')),
    ('UZ', _('Uzbekistan')),
    ('VA', _('Vatican City State (Holy See)')),
    ('VC', _('St. Vincent & the Grenadines')),
    ('VE', _('Venezuela')),
    ('VG', _('British Virgin Islands')),
    ('VI', _('United States Virgin Islands')),
    ('VN', _('Viet Nam')),
    ('VU', _('Vanuatu')),
    ('WF', _('Wallis & Futuna Islands')),
    ('WS', _('Samoa')),
    ('YE', _('Yemen')),
    ('YT', _('Mayotte')),
    ('YU', _('Yugoslavia')),
    ('ZA', _('South Africa')),
    ('ZM', _('Zambia')),
    ('ZR', _('Zaire')),
    ('ZW', _('Zimbabwe')),
    ('ZZ', _('Unknown or unspecified country')),
)


def delete_all_settings_cache():
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, 'all']
    key = '.'.join(keys)
    cache.delete(key)


def cache_setting(scope, scope_category, name, value):
    """
    Caches a single setting within a scope
    and scope category
    """
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name]

    key = '.'.join(keys)
    is_set = cache.add(key, value)
    if not is_set:
        cache.set(key, value)


def cache_settings(scope, scope_category):
    """
    Caches all settings within a scope and scope category
    """
    filters = {
        'scope': scope,
        'scope_category': scope_category,
    }
    settings = Setting.objects.filter(**filters)
    if settings:
        for setting in settings:
            keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY,
                    setting.scope, setting.scope_category, setting.name]
            key = '.'.join(keys)
            is_set = cache.add(key, setting.get_value())
            if not is_set:
                cache.set(key, setting.get_value())


def delete_setting_cache(scope, scope_category, name):
    """
        Deletes a single setting within a
        scope and scope category
    """
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name]
    key = '.'.join(keys)
    cache.delete(key)


def delete_settings_cache(scope, scope_category):
    """
        Deletes all settings within a scope
        and scope category
    """
    filters = {
        'scope': scope,
        'scope_category': scope_category,
    }
    settings = Setting.objects.filter(**filters)
    for setting in settings:
        keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY,
                setting.scope, setting.scope_category, setting.name]
        key = '_'.join(keys)
        cache.delete(key)


def get_setting(scope, scope_category, name):
    """
        Gets a single setting value from within a scope
        and scope category.
        Returns the value of the setting if it exists
        otherwise it returns an empty string
    """
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name]
    key = '.'.join(keys)

    setting = cache.get(key)

    if not setting:
        #setting is not in the cache
        try:
            #try to get the setting and cache it
            filters = {
                'scope': scope,
                'scope_category': scope_category,
                'name': name
            }
            setting = Setting.objects.get(**filters)
            cache_setting(setting.scope, setting.scope_category, setting.name, setting)
        except Exception:
            setting = None

    #check if the setting has been set and evaluate the value
    if setting:
        value = setting.get_value().strip()
        # convert data types
        if setting.data_type == 'boolean':
            value = value[0].lower() == 't'
        if setting.data_type == 'int':
            if value.strip():
                value = int(value.strip())
            else:
                value = 0  # default to 0
        if setting.data_type == 'file':
            from tendenci.core.files.models import File as TFile
            try:
                tfile = TFile.objects.get(pk=value)
            except TFile.DoesNotExist:
                tfile = None
            value = tfile
        return value

    return u''


def get_global_setting(name):
    return get_setting('site', 'global', name)


def get_module_setting(scope_category, name):
    return get_setting('module', scope_category, name)


def check_setting(scope, scope_category, name):
    #check cache first
    keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name]
    key = '.'.join(keys)

    setting = cache.get(key)
    if setting:
        return True

    missing_keys = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, scope,
            scope_category, name, "missing"]
    missing_key = '.'.join(missing_keys)

    missing = cache.get(missing_key)
    if not missing:
        #check the db if it is not in the cache
        exists = Setting.objects.filter(scope=scope,
            scope_category=scope_category, name=name).exists()

        #cache that it does not exist
        if not exists:
            #set to True to signify that it is missing so we do not
            #come back into this if statement and query db again
            is_set = cache.add(missing_key, True)
            if not is_set:
                cache.set(missing_key, True)

        return exists
    return False


def get_form_list(user):
    """
    Generate a list of 2-tuples of form id and form title
    This will be used as a special select
    """
    from tendenci.apps.forms_builder.forms.models import Form
    from tendenci.core.perms.utils import get_query_filters
    filters = get_query_filters(user, 'forms.view_form')
    forms = Form.objects.filter(filters)
    #To avoid hitting the database n time by calling .object
    #We will use the values in the index field.
    l = []
    for form in forms:
        l.append((form.pk, form.title))

    return l


def get_box_list(user):
    """
    Generate a list of 2-tuples of form id and form title
    This will be used as a special select
    """
    from tendenci.apps.boxes.models import Box
    from tendenci.core.perms.utils import get_query_filters
    filters = get_query_filters(user, 'boxes.view_box')
    boxes = Box.objects.filter(filters)
    #To avoid hitting the database n time by calling .object
    #We will use the values in the index field.
    l = [('', 'None')]
    for box in boxes:
        l.append((box.pk, box.title))

    return l


def get_group_list(user):
    """
    Generate a list of 2-tuples of group id and group name
    This will be used as a special select
    """
    from tendenci.apps.user_groups.models import Group
    groups = Group.objects.filter(status=True,
                                  status_detail='active'
                                  ).exclude(type='system_generated'
                                  ).order_by('name')
    if not groups.exists():
        # no groups - create one
        groups = [Group.objects.get_or_create_default(user)]
        initial_group = groups[0]
    else:
        [initial_group] = groups.filter(
                        entity__id=1,
                        entity__entity_name__iexact=get_global_setting(
                                                    'sitedisplayname')
                        )[:1] or [None]
        if not initial_group:
            [initial_group] = groups.filter(
                        entity__id=1)[:1] or [None]
        if not initial_group:
            initial_group = groups[0]

    choices = []

    for group in groups:
        choices.append((group.pk, group.name))

    return choices, initial_group.id

