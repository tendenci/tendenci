import os
import shutil
import sys
from tempfile import mkstemp

from shutil import move
from os import remove, close

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.utils.importlib import import_module

from tendenci.core.theme.utils import get_theme_root
from tendenci.contrib.theme_editor.models import ThemeFileVersion
from tendenci.libs.boto_s3.utils import save_file_to_s3


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
)

# At compile time, cache the directories to search.
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_templates = {}
for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app)
    except ImportError, e:
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
                dir_list.append(os.path.join(pwd,item))
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
        subdir = {'contents': []}
        folders = path[start:].split(os.sep)
        for f in files:
            editable = False
            if os.path.splitext(os.path.join(path,f))[1] in ALLOWED_EXTENSIONS:
                editable = True
            subdir['contents'].append({'name': f,'path': os.path.join(path[len(root_dir)+1:],f), 'editable': editable})
        parent = reduce(dict.get, folders[:-1], files_folders)
        parent[folders[-1]] = subdir
        for parent in files_folders:
            subdir['contents'].append({'folder_path': path})

    return files_folders

def get_file_content(file, ROOT_DIR=THEME_ROOT):
    """
    Get the content from the file that selected from
    the navigation
    """
    content = ''
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

def handle_uploaded_file(f, file_dir):
    file_path = os.path.join(file_dir, f.name)
    destination = open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    
    # copy to s3
    if settings.USE_S3_STORAGE:
        if os.path.splitext(f.name)[1] == '.html':
            public = False
        else:
            public = True
        save_file_to_s3(file_path, public=public)
    
    
    
