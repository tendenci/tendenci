from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe

def _add_name_to_class_attr(name, kwargs_dict):
    if "attrs" in kwargs_dict:
        if "class" in kwargs_dict["attrs"]:
            kwargs_dict["attrs"]["class"] += " %s" % (name.replace("_", "-"), )
        else:
            kwargs_dict["attrs"].update({'class': name.replace("_", "-")})
    else:
        kwargs_dict["attrs"] = {'class': name.replace("_", "-")}

    return kwargs_dict

def _strip_name_attr(widget_string, name):
    return widget_string.replace("name=\"%s\"" % (name,), "")


class NoNameTextInput(TextInput):
    def render(self, name, *args, **kwargs):
        kwargs = _add_name_to_class_attr(name, kwargs)
        return mark_safe(_strip_name_attr(super(NoNameTextInput, self).render(name, *args, **kwargs), name))
