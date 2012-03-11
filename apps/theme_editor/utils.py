import os
import shutil
from tempfile import mkstemp
from shutil import move
from os import remove, close

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management import call_command

from theme.utils import get_theme_root
from theme_editor.models import ThemeFileVersion

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

def copy(path_to_file, file, FROM_ROOT=TEMPLATES_ROOT, TO_ROOT=THEME_ROOT, plugin=None):
    """
        Copies a file and all associated directories into TO_ROOT
    """
    try:
        os.makedirs(os.path.join(TO_ROOT, "templates", path_to_file))
    except OSError:
        pass
    full_filename = os.path.join(path_to_file, file)
    if plugin:
        FROM_ROOT = os.path.join(settings.PROJECT_ROOT, "plugins", plugin, 'templates')
    shutil.copy(os.path.join(FROM_ROOT, full_filename), os.path.join(TO_ROOT, "templates", full_filename))

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

def get_dir_list(pwd, ROOT_DIR=THEME_ROOT, include_plugins=False):
    """
    Get a list of directories from within
    the theme folder based on the present
    working directory
    if the pwd is the None this will include a list of plugins in
    the dir_list.
    """
    dir_list = []
    if pwd.startswith("plugins.") and include_plugins:
        plugin_name = pwd.split('plugins.')[1].split('/')[0]
        current_dir = os.path.join(settings.PROJECT_ROOT, "plugins",
            plugin_name, 'templates', pwd.split('plugins.')[1])
    else:
        current_dir = os.path.join(ROOT_DIR, pwd)
    
    if include_plugins and not pwd:
        import pluginmanager
        plugins = pluginmanager.plugin_apps(())
        for plugin in plugins:
            dir_list.append(plugin)
    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
        for item in item_list:
            current_item = os.path.join(current_dir, item)
            if os.path.isdir(current_item):
                dir_list.append(os.path.join(pwd,item))
    return sorted(dir_list)

def get_file_list(pwd, ROOT_DIR=THEME_ROOT, include_plugins=False):
    """
    Get a list of files from within
    the theme folder based on the present
    working directory
    """
    file_list = []
    others_list = []
    if pwd.startswith("plugins.") and include_plugins:
        plugin_name = pwd.split('plugins.')[1].split('/')[0]
        current_dir = os.path.join(settings.PROJECT_ROOT, "plugins",
            plugin_name, 'templates', pwd.split('plugins.')[1])
    else:
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


def handle_uploaded_file(f, file_dir="templates", ROOT_DIR=THEME_ROOT):
    file_path = os.path.join(ROOT_DIR, file_dir, f.name)
    print file_path
    destination = open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
