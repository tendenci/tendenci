import os
import shutil
import sys
import boto
import urllib
from datetime import datetime
from dateutil.parser import parse
from operator import itemgetter

from django.conf import settings
from django.core.cache import cache
from importlib import import_module

from tendenci.apps.theme.utils import get_theme_root, get_theme
from tendenci.apps.theme_editor.models import ThemeFileVersion
from tendenci.libs.boto_s3.utils import save_file_to_s3, read_theme_file_from_s3
from functools import reduce


template_directory = "/templates"
style_directory = "/media/css"

THEME_ROOT = get_theme_root()
TEMPLATES_ROOT = os.path.join(settings.PROJECT_ROOT, "templates")
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

DEFAULT_THEME_INFO = 'theme.info'

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

        theme_root = get_theme_root(theme)
        # check if theme info file exists
        is_file = qstr_is_file(DEFAULT_THEME_INFO, ROOT_DIR=theme_root)
        if is_file:
            theme_file = file(os.path.join(theme_root, DEFAULT_THEME_INFO))
            data = theme_file.readlines()
            theme_file.close()
            # set attributes according to data in info file
            for datum in data:
                datum = datum.replace('\n', '')
                if "=" in datum:
                    label, value = datum.split('=', 1)
                    label = label.strip().replace(' ', '_').lower()
                    value = value.strip()

                    if label == 'create_dt':
                        value = parse(value)

                    if label in ('screenshot', 'screenshot_thumbnail'):
                        value = os.path.join('/themes', theme, value)

                    setattr(self, label, value)

# At compile time, cache the directories to search.
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_templates = {}
for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app)
    except ImportError as e:
        raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        app_templates[app] = template_dir.decode(fs_encoding)


def copy(filename, path_to_file, full_filename, TO_ROOT=THEME_ROOT):
    """Copies a file and all associated directories into TO_ROOT
    """
    try:
        os.makedirs(os.path.join(TO_ROOT, "templates", path_to_file))
    except OSError:
        pass

    filecopy = os.path.join(TO_ROOT, "templates", path_to_file, filename)
    shutil.copy(full_filename, filecopy)

    # copy to s3
    if settings.USE_S3_THEME:
        if os.path.splitext(filename)[1] == '.html':
            public = False
        else:
            public = True
        dest_path = "/themes/%s" % filecopy
        save_file_to_s3(full_filename, dest_path=dest_path, public=public)


def qstr_is_dir(query_string, ROOT_DIR=THEME_ROOT):
    """
    Check to see if the query string is a directory or not
    """
    current_dir = os.path.join(ROOT_DIR, query_string)
    return os.path.isdir(current_dir)


def qstr_is_file(query_string, ROOT_DIR=THEME_ROOT):
    """
    Check to see if the query string is a directory or not
    """
    if settings.USE_S3_THEME:
        content = get_file_content(query_string)
        if content:
            return True

    current_file = os.path.join(ROOT_DIR, query_string)
    return os.path.isfile(current_file)


def get_dir_list(pwd, ROOT_DIR=THEME_ROOT):
    """
    Get a list of directories from within
    the theme folder based on the present
    working directory
    if the pwd is the None this will include a list of plugins in
    the dir_list.
    """
    dir_list = []
    current_dir = os.path.join(ROOT_DIR, pwd)
    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
        for item in item_list:
            current_item = os.path.join(current_dir, item)
            if os.path.isdir(current_item):
                dir_list.append(os.path.join(pwd, item))
    return sorted(dir_list)


def get_file_list(pwd, ROOT_DIR=THEME_ROOT):
    """
    Get a list of files from within
    the theme folder based on the present
    working directory
    """
    file_list = []
    others_list = []
    current_dir = os.path.join(ROOT_DIR, pwd)
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


def get_all_files_list(ROOT_DIR=THEME_ROOT):
    """
    Get a list of files and folders from within
    the theme folder
    """
    files_folders = {}
    root_dir = os.path.join(ROOT_DIR)

    start = root_dir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(root_dir):
        folders = path[start:].split(os.sep)

        # Hide hidden folders and folders within hidden folders
        if any(folder.startswith('.') for folder in folders):
            continue

        subdir = {'contents': []}
        for f in files:
            editable = False
            if os.path.splitext(os.path.join(path, f))[1] in ALLOWED_EXTENSIONS:
                editable = True

            # Hide hidden files
            if not f.startswith('.'):
                subdir['contents'].append({'name': f, 'path': os.path.join(path[len(root_dir) + 1:], f), 'editable': editable})

        subdir['contents'] = sorted(subdir['contents'], key=itemgetter('name'))
        subdir['contents'].append({'folder_path': path})
        parent = reduce(dict.get, folders[:-1], files_folders)
        parent[folders[-1]] = subdir

    if settings.USE_S3_THEME:
        s3_files_folders = {'contents': []}
        theme_folder = "%s/%s" % (settings.THEME_S3_PATH, get_theme())
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                               settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        for item in bucket.list(prefix=theme_folder):

            editable = False
            if os.path.splitext(item.name)[1] in ALLOWED_EXTENSIONS:
                editable = True

            file_path = item.name.replace(theme_folder, '').lstrip('/')
            path_split = file_path.split('/')
            splits = len(path_split)

            if splits == 1:
                s3_files_folders['contents'].append({
                        'name': path_split[0],
                        'path': file_path,
                        'editable': editable})
            elif splits == 2:
                if not path_split[0] in s3_files_folders:
                    s3_files_folders[path_split[0]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

                s3_files_folders[path_split[0]]['contents'].append({
                        'name': path_split[1],
                        'path': file_path,
                        'editable': editable})
            elif splits == 3:
                if not path_split[0] in s3_files_folders:
                    s3_files_folders[path_split[0]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

                if not path_split[1] in s3_files_folders[path_split[0]]:
                    s3_files_folders[path_split[0]][path_split[1]] = {'contents': [{'folder_path': "/".join(path_split[:-1])}]}

                s3_files_folders[path_split[0]][path_split[1]]['contents'].append({
                        'name': path_split[2],
                        'path': file_path,
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
                        'editable': editable})

        return {get_theme(): s3_files_folders}

    return files_folders


def get_file_content(file, ROOT_DIR=THEME_ROOT):
    """
    Get the content from the file that selected from
    the navigation
    """
    content = ''

    if settings.USE_S3_THEME:
        try:
            theme = get_theme()
            content = read_theme_file_from_s3(os.path.join(theme, file))
        except:
            pass

    if not content:
        current_file = os.path.join(ROOT_DIR, file)
        if os.path.isfile(current_file):
            fd = open(current_file, 'r')
            content = fd.read()
            fd.close()
    return content


def archive_file(request, relative_file_path, ROOT_DIR=THEME_ROOT):
    """
    Archive the file into the database if it is edited
    """
    file_path = os.path.join(ROOT_DIR, relative_file_path)
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


def handle_uploaded_file(file_path, file_dir):
    file_name = os.path.basename(file_path)
    filecopy = os.path.join(THEME_ROOT, file_dir, file_name)
    dest_path = os.path.join(settings.PROJECT_ROOT, "themes", filecopy)

    shutil.move(file_path, dest_path)

    # copy to s3
    if settings.USE_S3_THEME:
        if os.path.splitext(f.name)[1] == '.html':
            public = False
        else:
            public = True
        dest_path = "/themes/%s" % filecopy
        save_file_to_s3(file_path, dest_path=dest_path, public=public)

        cache_key = ".".join([settings.SITE_CACHE_KEY, 'theme', file_path[(file_path.find(THEME_ROOT)):]])
        cache.delete(cache_key)

        if hasattr(settings, 'REMOTE_DEPLOY_URL') and settings.REMOTE_DEPLOY_URL:
            urllib.urlopen(settings.REMOTE_DEPLOY_URL)
