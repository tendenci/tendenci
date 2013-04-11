from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from tendenci.apps.profiles.models import Profile
from tendenci.apps.profiles.forms import ProfileAdminForm

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'display_name', 'get_email')
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
        (_('Login Information'), {'fields': ('username',
                                             'password1',
                                             'password2',
                                             'interactive',
                                             'status_detail',
                                             'status',)}),
        (_('Notes'), {'fields': ('notes',)}),
        (_('Optional Information'), {'fields': ('time_zone',
                                                'language',
                                                'spouse',
                                                'dob',
                                                'sex',)}),
        (_('Administrator Information'), {'fields': ('admin_notes',
                                                     'security_level',)}),)
    form = ProfileAdminForm

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
            obj.creator_username = request.user.username
        obj.owner = request.user
        obj.owner_username = request.user.username

        obj.save()

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field  = 'user__email'
    get_email.short_description = 'Email'

    def get_user(self, obj):
        name = "%s %s" % (obj.user.first_name, obj.user.last_name)
        name = name.strip()

        return name or obj.user.username
    get_user.short_description = 'User'

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
#admin.site.register(User, MyUserAdmin)
