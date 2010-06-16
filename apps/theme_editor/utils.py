import os

from django.conf import settings
from django.core.urlresolvers import reverse

from theme_editor.models import ThemeFileVersion

template_directory = "/templates"
style_directory = "/media/css"

def get_file_content(file_path):
    file_content = ""
    if os.path.isfile(file_path):
        fd = open(file_path, 'r')
        file_content = fd.read()
        fd.close()
    return file_content

def get_file_attr(file_path):
    file_dict = {"name":"", "type": ""}
    if os.path.isfile(file_path):
        (file_dir, file_name) = os.path.split(file_path)
        file_dict["name"] = file_name
        (file_basename, file_ext) = os.path.splitext(file_name)
        if file_ext == ".css":
           file_dict["type"] = "Stylesheet"
        if file_ext == ".html":
           file_dict["type"] = "Template"
                
    return file_dict

def get_files_list(theme_root):
    files_list = {"templates":[], "styles":[]}

    # template list
    template_folder_path = theme_root + template_directory
    tmp_files_list = os.listdir(template_folder_path)
    for item in tmp_files_list:
        if os.path.isfile(os.path.join(template_folder_path, item)):
            link = '<a href=\"%s?file=%s/%s">%s</a>' % (reverse('theme_editor'),
                                                        template_directory,
                                                        item,
                                                        item)
            files_list["templates"].append(link)
   
    # style list
    style_folder_path = theme_root + style_directory
    tmp_files_list = os.listdir(style_folder_path)
    for item in tmp_files_list:
        if os.path.isfile(os.path.join(style_folder_path, item)):
            (base, ext) = os.path.splitext(item)
            if ext == ".css":
                link = '<a href=\"%s?file=%s/%s">%s</a>' % (reverse('theme_editor'),
                                                            style_directory,
                                                            item,
                                                            item)
                files_list["styles"].append(link)
                
    return files_list

def archive_file(request, relative_file_path):
    file_path = (os.path.join(settings.THEME_ROOT, relative_file_path)).replace("\\", "/")
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