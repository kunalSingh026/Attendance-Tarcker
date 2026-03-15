# attendance/templatetags/my_filters.py
from django import template

register = template.Library()

@register.simple_tag
def today_date():
    """Return today's date string (YYYY-MM-DD)"""
    from datetime import date
    return date.today().isoformat()

@register.filter
def to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default
