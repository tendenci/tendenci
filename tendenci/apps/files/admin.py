from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.core.files.models import File, MultipleFile, FilesCategory
from tendenci.core.files.forms import FileForm, MultiFileForm, FilewithCategoryForm, FileCategoryForm


class FileAdmin(TendenciBaseModelAdmin):
    list_display = ['file_preview', 'name', 'file_path', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status', 'owner_username']
    prepopulated_fields = {}
    search_fields = ['file', 'tags']
    fieldsets = (
        (_('File Information'), {
            'fields': ('file',
                       'name',
                       'tags',
                       'group',
                       )
        }),
        (_('Category'), {'fields': ('file_cat', 'file_sub_cat')}),
        (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
        (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
    )
    form = FilewithCategoryForm
    ordering = ['-update_dt']
    actions = ['add_to_category_and_subcategory']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
            '%sjs/categories.js' % settings.STATIC_URL,
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        filecategory_form = FileCategoryForm()
        extra_context.update({'filecategory_form' : filecategory_form})

        return super(FileAdmin, self).changelist_view(request, extra_context)

    def file_preview(self, obj):
        if obj.type() == "image":
            if obj.file:
                args = [obj.pk]
                args.append("100x50")
                args.append("crop")
                return '<img alt="%s" title="%s" src="%s" />' % (obj, obj, reverse('file', args=args))
            else:
                return ""
        elif obj.icon():
            return '<img alt="%s" title="%s" src="%s" />' % (obj.type(), obj.type(), obj.icon())
        else:
            return obj.type()
    file_preview.allow_tags = True
    file_preview.short_description = _('Preview')

    def file_path(self, obj):
        return obj.file
    file_path.short_description = _("File Path")

    def add_to_category_and_subcategory(self, request, queryset):
        count = queryset.count()
        filecategory_form = FileCategoryForm(request.POST)

        if filecategory_form.is_valid():
            for file in queryset:
                filecategory_form.update_file_cat_and_sub_cat(file)

        if count > 1:
            messages.success(request, _("Successfully updated Category/Sub Category of %(c)s files." % {'c':count}))
        elif count == 1:
            messages.success(request, _("Successfully updated Category/Sub Category of a file."))

    add_to_category_and_subcategory.short_description = _('Add to category')

admin.site.register(File, FileAdmin)


class MultipleFileAdmin(admin.ModelAdmin):

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(MultipleFileAdmin, self).get_urls()
        extra_urls = patterns("",
            url("^add",
                self.admin_site.admin_view(self.add_multiple_file_view),
                name="multiplefile_add"),
        )
        return extra_urls + urls

    def add_multiple_file_view(self, request):
        form = MultiFileForm(request=request)

        if request.method == 'POST':
            form = MultiFileForm(request.POST, request.FILES, request=request)
            if form.is_valid():
                counter = form.save()
                if counter == 1:
                    messages.success(request, _('Successfully uploaded a file.'))
                elif counter > 1:
                    string = 'Successfully uploaded %s files.' % counter
                    messages.success(request, _(string) )
                return redirect(reverse('admin:files_file_changelist'))
        return render(request,
            'admin/files/file/multiple_file_upload.html',{
            'adminform': form
        });

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('admin:multiplefile_add'))

admin.site.register(MultipleFile, MultipleFileAdmin)



class CategoryAdminInline(admin.TabularInline):
    fieldsets = ((None, {'fields': ('name',)}),)
    model = FilesCategory
    extra = 0
    verbose_name = _("File Sub-Category")
    verbose_name_plural = _("File Sub-Categories")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fieldsets = ((None, {'fields': ('name',)}),)
    inlines = (CategoryAdminInline,)

    def queryset(self, request):
        qs = super(CategoryAdmin, self).queryset(request)
        return qs.filter(parent__isnull=True)

admin.site.register(FilesCategory, CategoryAdmin)
