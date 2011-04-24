import os

import shutil

from django.conf import settings
from django.core.urlresolvers import reverse

from theme_editor.models import ThemeFileVersion

template_directory = "/templates"
style_directory = "/media/css"

THEME_ROOT = settings.THEME_ROOT
ALLOWED_EXTENSIONS = (
    '.html',
    '.css',
    '.txt',
    '.js'
)

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
    return dir_list

def get_file_list(pwd, ROOT_DIR=THEME_ROOT):
    """
    Get a list of files from within
    the theme folder based on the present
    working directory
    """
    file_list = []
    current_dir = os.path.join(ROOT_DIR, pwd)
    if os.path.isdir(current_dir):
        item_list = os.listdir(current_dir)
        for item in item_list:
            current_item = os.path.join(current_dir, item)
            if os.path.isfile(current_item):
                if os.path.splitext(current_item)[1] in ALLOWED_EXTENSIONS:
                    file_list.append(item)
        return sorted(file_list)
    return file_list

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

def archive_file(request, relative_file_path):
    """
    Archive the file into the database if it is edited
    """
    file_path = os.path.join(settings.THEME_ROOT, relative_file_path)
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
