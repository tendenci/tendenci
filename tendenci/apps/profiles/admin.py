from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.core.perms.utils import update_perms_and_save
from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.forms import ProfileAdminForm


class ProfileAdmin(TendenciBaseModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'get_email', 'is_active', 'is_superuser')
    search_fields = ('display_name', 'user__first_name', 'user__last_name', 'user__username', 'user__email')

    fieldsets = (
        (_('Name Information'), {'fields': ('salutation',
                                            'first_name',
                                            'initials',
                                            'last_name',
                                            'position_title',
                                            'display_name',
                                            'hide_in_search',)}),
        (_('Phone Information'), {'fields': ('phone',
                                             'phone2',
                                             'fax',
                                             'work_phone',
                                             'home_phone',
                                             'mobile_phone',
                                             'hide_phone',)}),
        (_('E-mail and Internet Information'), {'fields': ('email',
                                                           'email2',
                                                           'url',
                                                           'hide_email',)}),
        (_('Company Information'), {'fields': ('company',
                                               'department',)}),
        (_('Address Information'), {'fields': ('mailing_name',
                                               'address',
                                               'address2',
                                               'city',
                                               'state',
                                               'zipcode',
                                               'country',
                                               'hide_address',)}),
        (_('Alternate Address Information'), {'fields': ('address_2',
                                               'address2_2',
                                               'city_2',
                                               'state_2',
                                               'zipcode_2',
                                               'country_2',)}),
        (_('Login Information'), {'fields': ('username',
                                             'password1',
                                             'password2',
                                             'interactive',
                                             'status_detail',)}),
        (_('Notes'), {'fields': ('notes',)}),
        (_('Optional Information'), {'fields': ('time_zone',
                                                'language',
                                                'spouse',
                                                'dob',
                                                'sex',)}),
        (_('Administrator Information'), {'fields': ('admin_notes',
                                                     'security_level',)}),)
    form = ProfileAdminForm

    ordering = ('user__last_name', 'user__first_name')
    
    def get_object(self, request, object_id):
        obj = super(ProfileAdmin, self).get_object(request, object_id)
        # Avoid language being accidentally set to the first option 'ar'
        # because en-us is not an option in the language dropdown
        if obj and obj.language == 'en-us':
            obj.language = 'en'
        return obj

    def save_model(self, request, object, form, change):
        instance = form.save(request=request, commit=False)
        instance = update_perms_and_save(request, form, instance, log=False)

        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        EventLog.objects.log(**log_defaults)
        return instance

    def save_form(self, request, form, change):
        return form.save(request=request, commit=False)

    def get_email(self, obj):
        return obj.user.email

    get_email.admin_order_field = 'user__email'
    get_email.short_description = _('Email')

    def is_superuser(self, obj):
        return obj.is_superuser
    is_superuser.boolean = True

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True

    def get_user(self, obj):
        name = "%s %s" % (obj.user.first_name, obj.user.last_name)
        name = name.strip()

        return name or obj.user.username
    get_user.short_description = _('User')

admin.site.register(Profile, ProfileAdmin)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        # Removing the permission part
        # (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Permissions'), {'fields': ('user_permissions',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
