from django.template import Library

register = Library()

@register.filter()
def sortcontents(value):
    """
    Takes a list of folders and files, sorts the folder, and moves the files to the bottom.
    """
    ordered = sorted(value)
    contents_index = [i for i,x in enumerate(ordered) if x[0] == 'contents'][0]
    if len(ordered) > 1:
        contents = ordered[contents_index]
        ordered.pop(contents_index)
        ordered.append(contents)

    return ordered