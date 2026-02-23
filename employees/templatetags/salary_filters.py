from django import template

register = template.Library()

@register.filter
def star_format(value):
    """
    Convert numeric value to star format for privacy
    Example: 50000 becomes ₹50,***
    """
    if not value:
        return '₹0'
    
    try:
        # Convert to float and handle negative values
        num_value = float(value)
        if num_value < 0:
            return f'-₹{abs(int(num_value)):,}***'
        
        # Format with comma separator and add stars
        formatted = f'₹{int(num_value):,}***'
        return formatted
    except (ValueError, TypeError):
        return str(value)

@register.filter
def reveal_format(value):
    """
    Convert numeric value to proper currency format
    """
    if not value:
        return '₹0'
    
    try:
        num_value = float(value)
        if num_value < 0:
            return f'-₹{abs(int(num_value)):,}'
        
        formatted = f'₹{int(num_value):,}'
        return formatted
    except (ValueError, TypeError):
        return str(value)

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the argument
    Usage: {{ value|multiply:12 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
