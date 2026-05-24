from django import template

register = template.Library()


@register.filter(name='split')
def split_string(value, delimiter=','):
    """
    Stringni delimiter bo'yicha bo'ladi.
    Ishlatilishi: {{ "a,b,c"|split:"," }}
    """
    return [item.strip() for item in value.split(delimiter)]
