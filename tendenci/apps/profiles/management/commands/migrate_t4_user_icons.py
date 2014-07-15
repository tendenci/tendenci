import mimetypes
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from avatar.models import Avatar, avatar_file_path

class Command(BaseCommand):
    """
    Migrate users' icons by searching the File's module.

    Usage: python manage.py migrate_t4_user_icons
    """

    def handle(self, *args, **options):
        from tendenci.core.files.models import File as tFile

        ct_user = ContentType.objects.get_for_model(User)
        tfiles = tFile.objects.filter(content_type=ct_user,
                                      object_id__isnull=False,
                                      status=True,
                                      status_detail='active')
        for tfile in tfiles:
            if default_storage.exists(tfile.file.name):
                is_image = mimetypes.guess_type(tfile.file.name)[0].startswith('image')
                if is_image:
                    [user] = User.objects.filter(id=tfile.object_id)[:1] or [None]
                    if user:
                        [user_avatar] = user.avatar_set.filter(
                                                primary=True)[:1] or [None]
                        if not user_avatar:
                            avatar_path = avatar_file_path(
                                                    user=user,
                                                    filename=(tfile.file.name.split('/'))[-1])
                            # copy the file to the avatar directory
                            default_storage.save(avatar_path,
                                                  ContentFile(
                                                   default_storage.open(
                                                    tfile.file.name).read()))
                            # create an avatar object for the user
                            Avatar.objects.create(
                                user=user,
                                primary=True,
                                avatar=avatar_path
                                    )
                            print 'Avatar created for ', user
        print 'Done'
