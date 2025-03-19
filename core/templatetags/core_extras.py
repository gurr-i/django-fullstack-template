from django import template

register = template.Library()

@register.filter
def unread_count(notifications):
    """Return the count of unread notifications."""
    return notifications.filter(is_read=False).count()

@register.filter
def replace(value, arg):
    """Replace all occurrences of the first argument with the second argument."""
    if len(arg.split(',')) != 2:
        return value
    
    old, new = arg.split(',')
    return value.replace(old, new)