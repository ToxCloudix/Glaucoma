import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def json_script(value):
    """
    Преобразует объект Python в JSON-строку и помечает её как безопасную для HTML.
    """
    return mark_safe(json.dumps(value))