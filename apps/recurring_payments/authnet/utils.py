
import re


def to_camel_case(d):
    """
	Convert all keys in d dictionary from underscore_format to
	camelCaseFormat and return the new dict
	"""
    if type(d) is dict:
        to_upper = lambda match: match.group(1).upper()
        to_camel = lambda x: re.sub("_([a-z])", to_upper, x)
        
        return dict(map(lambda x: (to_camel(x[0]), x[1]), d.items()))
    return d

