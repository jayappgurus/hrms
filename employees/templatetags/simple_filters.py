from django import template

register = template.Library()

@register.filter
def add_commas(value):
    """Add commas to number for display"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)
