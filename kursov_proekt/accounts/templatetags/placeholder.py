from django import template

register = template.Library()

@register.filter(name='placeholder')
def set_placeholder(field, placeholder_value):
    """
    Adds a placeholder attribute to the form field widget.
    """
    if field.field.widget.attrs.get('placeholder') is None:
        field.field.widget.attrs['placeholder'] = placeholder_value
    return field
