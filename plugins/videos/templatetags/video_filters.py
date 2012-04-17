from django.template import Library
register = Library()

@register.filter     
def assign_mapped_fields(obj):
    """assign mapped field from custom registration form to registrant"""
    if hasattr(obj, 'custom_reg_form_entry') and obj.custom_reg_form_entry:
        obj.assign_mapped_fields()
    return obj

@register.filter
def video_embed(video, width):
	"""
	Return a video at the specified width
	"""
	from django.template.defaultfilters import safe
	return safe(video.embed_code(width=width))


