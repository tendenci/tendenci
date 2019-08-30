from django.conf.urls import url
from django.contrib import admin, messages
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.files.models import File, MultipleFile, FilesCategory
from tendenci.apps.files.forms import MultiFileForm, FilewithCategoryForm, FileCategoryForm
from tendenci.apps.theme.templatetags.static import static


class FileAdmin(TendenciBaseModelAdmin):
    list_display = ['file_preview', 'name', 'file_cat', 'file_path', 'owner_link', 'admin_perms', 'admin_status']
    list_filter = ['status', ('file_cat', admin.RelatedOnlyFieldListFilter), 'owner_username']
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
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            static('js/categories.js'),
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        filecategory_form = FileCategoryForm()
        extra_context.update({'filecategory_form' : filecategory_form})

        return super(FileAdmin, self).changelist_view(request, extra_context)

    @mark_safe
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
        extra_urls = [
            url("^add",
                self.admin_site.admin_view(self.add_multiple_file_view),
                name="multiplefile_add"),
        ]
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
        return render_to_resp(request=request,
            template_name='admin/files/file/multiple_file_upload.html',
            context={
            'adminform': form
        })

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
    list_display = ('id', 'name',)
    list_display_links = ('name',)
    fieldsets = ((None, {'fields': ('name',)}),)
    inlines = (CategoryAdminInline,)

    def queryset(self, request):
        qs = super(CategoryAdmin, self).queryset(request)
        return qs.filter(parent__isnull=True)

admin.site.register(FilesCategory, CategoryAdmin)
