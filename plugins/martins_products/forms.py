import imghdr
from os.path import splitext

from django import forms
from django.utils.translation import ugettext_lazy as _

from martins_products.models import Product, Category, Formulation, ProductPhoto, HoverPhoto
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)


class ProductForm(TendenciBaseForm):
    class Meta:
        model = Product

    status_detail = forms.ChoiceField(choices=(('active', 'Active'), ('pending', 'Pending')))
    generic_description = forms.CharField(required=True,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': u'martins_products',
        'storme_model': Product._meta.module_name.lower()}))
    product_features = forms.CharField(required=True,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': u'martins_products',
        'storme_model': Product._meta.module_name.lower()}))
    product_specs = forms.CharField(required=True,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': u'martins_products',
        'storme_model': Product._meta.module_name.lower()}))
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    hover_photo_upload = forms.FileField(label=_('Hover Photo'), required=False)
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['generic_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['product_features'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['product_specs'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['generic_description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['product_features'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['product_specs'].widget.mce_attrs['app_instance_id'] = 0
            
    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        print 'clean photo_upload', photo_upload

        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo must be of jpg, gif, or png image type.')

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo is an invalid image. Try uploading another photo.')

        return photo_upload
    
    def clean_hover_photo_upload(self):
        hover_photo_upload = self.cleaned_data['hover_photo_upload']
        print 'clean hover_photo_upload', hover_photo_upload

        if hover_photo_upload:
            extension = splitext(hover_photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo must be of jpg, gif, or png image type.')

            # check the image header
            image_type = '.%s' % imghdr.what('', hover_photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo is an invalid image. Try uploading another photo.')

        return hover_photo_upload
    
    def save(self, *args, **kwargs):
        product = super(ProductForm, self).save(*args, **kwargs)
        photo_upload = self.cleaned_data.get('photo_upload')
        hover_photo_upload = self.cleaned_data.get('hover_photo_upload')
        
        if photo_upload:
            image = ProductPhoto(
                        creator = product.owner,
                        creator_username = product.owner_username,
                        owner = product.owner,
                        owner_username = product.owner_username
                    )
            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row

            if product.product_image:
                product.product_image.delete()  # delete image and file row
            product.product_image = image
        
        if hover_photo_upload:
            image = HoverPhoto(
                       creator = product.owner,
                       creator_username = product.owner_username,
                       owner = product.owner,
                       owner_username = product.owner_username
                    )
            image.file.save(hover_photo_upload.name, hover_photo_upload)  # save file row
            image.save()  # save image row

            if product.hover_image:
                product.hover_image.delete()  # delete image and file row
            product.hover_image = image                    
        return product


class ProductSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False,)
#    sub_category = CategoryField(label=_('Sub Category'), choices=[], required=False)
    formulation = forms.ModelChoiceField(queryset=Formulation.objects.all(), required=False,)

    def __init__(self, content_type, *args, **kwargs):
        super(ProductSearchForm, self).__init__(*args, **kwargs)

        # set up the category choices
        categories = Category.objects.all()
        categories = list(set([cat.name for cat in categories]))
        categories = [[cat, cat] for cat in categories]
        categories.insert(0, ['', '------------'])
        self.fields['category'].choices = tuple(categories)

        # set up the sub category choices
#        sub_categories = CategoryItem.objects.filter(content_type=content_type,
#                                                     category__exact=None)
#        sub_categories = list(set([cat.parent.name for cat in sub_categories]))
#        sub_categories = [[cat, cat] for cat in sub_categories]
#        sub_categories.insert(0, ['', '------------'])
#        self.fields['sub_category'].choices = tuple(sub_categories)
