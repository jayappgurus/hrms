from django import template

register = template.Library()

@register.filter
def splitlines(value):
    """Split a string by newlines and return a list"""
    if value:
        return value.splitlines()
    return []

@register.filter
def strip(value):
    """Strip whitespace from a string"""
    if value:
        return value.strip()
    return value
