import os, uuid
from django.db import models
from django.conf import settings
from perms.models import AuditingBaseModel
from django.contrib.contenttypes.models import ContentType

class File(AuditingBaseModel):
    file = models.FileField(upload_to='files')
    guid = models.CharField(max_length=200, default=uuid.uuid1)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    update_dt = models.DateTimeField(auto_now=True)
    create_dt = models.DateTimeField(auto_now_add=True)

    def basename(self):
        return os.path.basename(str(self.file))

    def type(self):
        ext = os.path.splitext(self.basename())[1].lower()

        # map file-type to extension
        types = {
            'image' : ('.jpg','.jpeg','.gif','.png','.tif','.tiff'),
            'text' : ('.txt','.doc','.docx'),
            'spreadsheet' : ('.csv','.xls','.xlsx'),
            'powerpoint' : ('.ppt','.pptx'),
            'pdf' : ('.pdf'),
            'video' : ('.wmv','.mov','.mpg'),
            'zip' : ('.zip'),
        }

        # if file ext. is recognized
        # return icon
        for type in types:
            if ext in types[type]:
                return type

        return None

    def icon(self):

        # if we don't know the type
        # we can't find an icon [to represent the file]
        if not self.type(): return None

        # assign icons directory
        icons_dir = os.path.join(settings.STATIC_URL, 'images/icons')

        # map file-type to image file
        icons = {
            'text': 'icon-ms-word-2007.gif',
            'spreadsheet': 'icon-ms-excel-2007.gif',
            'powerpoint': 'icon-ms-powerpoint-2007.gif',
            'image': 'icon-ms-image-2007.png',
            'pdf': 'icon-pdf.png',
            'video': 'icon-wmv.png',
            'zip': 'icon-zip.gif',
        }

        # return image path
        return icons_dir + '/' + icons[self.type()]

    class Meta:
        permissions = (("view_file","Can view file"),)

    def __unicode__(self):
        return self.name
