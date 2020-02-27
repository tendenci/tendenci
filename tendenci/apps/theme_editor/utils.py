import os
import shutil
import boto3
from urllib.request import urlopen
from datetime import datetime
from dateutil.parser import parse as parse_date
from operator import itemgetter
from functools import reduce

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils._os import safe_join
from django.core.exceptions import SuspiciousFileOperation
from importlib import import_module

from tendenci.apps.theme.utils import get_theme_root, get_theme_info, is_builtin_theme
from tendenci.apps.theme_editor.models import ThemeFileVersion
from tendenci.libs.boto_s3.utils import save_file_to_s3, read_theme_file_from_s3


template_directory = "/templates"
style_directory = "/media/css"

ALLOWED_EXTENSIONS = (
    '.html',
    '.css',
    '.txt',
    '.js',
    '.po',
    '.less',
    '.eot',
    '.ttf',
    '.woff',
    '.woff2',
    '.svg',
)


def is_valid_path(root, path):
    try:
        safe_join(root, path)
        return True
    except SuspiciousFileOperation:
        return False


def is_theme_read_only(theme):
    return is_builtin_theme(theme)


# Class to hold theme info details
class ThemeInfo(object):

    def __init__(self, theme):

        self.orig_name = theme
        self.name = theme
        self.description = u''
        self.tags = u''
        self.screenshot = u''
        self.screenshot_thumbnail = u''
        self.author = u''
        self.author_uri = u''
        self.version = u''
        self.create_dt = datetime.now()

        for label, value in get_theme_info(theme).get('General', {}).items():
            label = label.strip().replace(' ', '_').lower()
            if label == 'create_dt':
                value = parse_date(value)
            if label in ('screenshot', 'screenshot_thumbnail'):
                value = os.path.join('/themes', theme, value)
            setattr(self, label, value)


# At compile time, cache the directories to search.
app_templates = {}
for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app)
    except ImportError as e:
        raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        app_templates[app] = template_dir


def get_dir_list(root_dir, pwd):
    """
    Get a list of directories from within
    the theme folder based on the present
    working directory
    if the pwd is the None this will include a list of plugins in
    the dir_list.
    """
    dir_list = []
    current_dir = os.path.join(root_dir, pwd)
    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
        for item in item_list:
            current_item = os.path.join(current_dir, item)
            if os.path.isdir(current_item):
                dir_list.append(os.path.join(pwd, item))
    return sorted(dir_list)


def get_file_list(root_dir, pwd):
    """
    Get a list of files from within
    the theme folder based on the present
    working directory
    """
    file_list = []
    others_list = []
    current_dir = os.path.join(root_dir, pwd)
    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
        for item in item_list:
            current_item = os.path.join(current_dir, item)
            if os.path.isfile(current_item):
                if os.path.splitext(current_item)[1] in ALLOWED_EXTENSIONS:
                    file_list.append(item)
                elif os.path.splitext(current_item)[1]:
                    others_list.append(item)
        return sorted(file_list), sorted(others_list)
    return file_list, others_list


def get_all_files_list(root_dir, theme):
    """
    Get a list of files and folders from within
    the theme folder
    """
    files_folders = {}

    theme_base_url = '/themes/'+theme+'/'
    start = root_dir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(root_dir):
        folders = path[start:].split(os.sep)

        # Hide hidden folders and folders within hidden folders
        if any((folder.startswith('.') or folder in ('__pycache__', )) for folder in folders):
            continue

        subdir = {'contents': []}
        for f in files:
            editable = False
            if os.path.splitext(os.path.join(path, f))[1] in ALLOWED_EXTENSIONS:
                editable = True

            # Hide hidden files
            if not f.startswith('.'):
                file_path = os.path.join(path[len(root_dir) + 1:], f)
                file_url = theme_base_url+file_path
                subdir['contents'].append({'name': f, 'path': file_path, 'url': file_url, 'editable': editable})

        subdir['contents'] = sorted(subdir['contents'], key=itemgetter('name'))
        subdir['contents'].append({'folder_path': path})
        parent = reduce(dict.get, folders[:-1], files_folders)
        parent[folders[-1]] = subdir

    if not settings.USE_S3_THEME:
        return files_folders

    s3_files_folders = {'contents': []}
    theme_folder = settings.THEME_S3_PATH+'/'+theme
    theme_base_url = settings.AWS_LOCATION+'/'+theme_folder+'/'
    # Before using S3 storage, the AWS credentials should be set up https://pypi.org/project/boto3/
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    for item in bucket.objects.filter(Prefix=theme_folder):

        editable = False
        if os.path.splitext(item.name)[1] in ALLOWED_EXTENSIONS:
            editable = True

        file_path = item.name.replace(theme_folder, '').lstrip('/')
        file_url = theme_base_url+file_path
        path_split = file_path.split('/')
        splits = len(path_split)

        if splits == 1:
            s3_files_folders['contents'].append({
                    'name': path_split[0],
                    'path': file_path,
                    'url': file_url,
                    'editable': editable})
        elif splits == 2:
            if not path_split[0] in s3_files_folders:
                s3_files_folders[path_split[0]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

            s3_files_folders[path_split[0]]['contents'].append({
                    'name': path_split[1],
                    'path': file_path,
                    'url': file_url,
                    'editable': editable})
        elif splits == 3:
            if not path_split[0] in s3_files_folders:
                s3_files_folders[path_split[0]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

            if not path_split[1] in s3_files_folders[path_split[0]]:
                s3_files_folders[path_split[0]][path_split[1]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

            s3_files_folders[path_split[0]][path_split[1]]['contents'].append({
                    'name': path_split[2],
                    'path': file_path,
                    'url': file_url,
                    'editable': editable})
        elif splits == 4:
            if not path_split[0] in s3_files_folders:
                s3_files_folders[path_split[0]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

            if not path_split[1] in s3_files_folders[path_split[0]]:
                s3_files_folders[path_split[0]][path_split[1]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

            if not path_split[2] in s3_files_folders[path_split[0]][path_split[1]]:
                s3_files_folders[path_split[0]][path_split[1]][path_split[2]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

            s3_files_folders[path_split[0]][path_split[1]][path_split[2]]['contents'].append({
                    'name': path_split[3],
                    'path': file_path,
                    'url': file_url,
                    'editable': editable})

    return {theme: s3_files_folders}


def get_file_content(root_dir, theme, filename):
    """
    Get the content from the file that selected from
    the navigation
    """
    content = ''

    if settings.USE_S3_THEME:
        try:
            content = read_theme_file_from_s3(os.path.join(theme, filename))
        except:
            pass

    if not content:
        current_file = os.path.join(root_dir, filename)
        if os.path.isfile(current_file):
            fd = open(current_file, 'r')
            content = fd.read()
            fd.close()
    return content


def archive_file(root_dir, relative_file_path, request):
    """
    Archive the file into the database if it is edited
    """
    file_path = os.path.join(root_dir, relative_file_path)
    if os.path.isfile(file_path):
        (file_dir, file_name) = os.path.split(file_path)
        fd = open(file_path, 'r')
        content = fd.read()
        fd.close()
        archive = ThemeFileVersion(file_name=file_name,
                                  content=content,
                                  relative_file_path=relative_file_path,
                                  author=request.user)
        archive.save()


def copy_file_to_theme(source_full_path, to_theme, path_to_file, filename):
    """Copies a file and all associated directories into theme
    """
    root_dir = get_theme_root(to_theme)
    try:
        os.makedirs(os.path.join(root_dir, path_to_file))
    except OSError:
        pass
    dest_full_path = os.path.join(root_dir, path_to_file, filename)
    shutil.copy(source_full_path, dest_full_path)

    # copy to s3
    if settings.USE_S3_THEME:
        if os.path.splitext(filename)[1] == '.html':
            public = False
        else:
            public = True
        dest_path = os.path.join(to_theme, path_to_file, filename)
        dest_full_path = os.path.join(settings.THEME_S3_PATH, dest_path)
        save_file_to_s3(source_full_path, dest_path=dest_full_path, public=public)

        cache_key = ".".join([settings.SITE_CACHE_KEY, 'theme', dest_path])
        cache.delete(cache_key)

        if hasattr(settings, 'REMOTE_DEPLOY_URL') and settings.REMOTE_DEPLOY_URL:
            urlopen(settings.REMOTE_DEPLOY_URL)
