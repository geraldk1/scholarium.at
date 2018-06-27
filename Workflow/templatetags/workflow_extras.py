from django import template
register = template.Library()


@register.filter
def field_verbose_name(obj, field):
    return obj._meta.get_field(field).verbose_name.title()
