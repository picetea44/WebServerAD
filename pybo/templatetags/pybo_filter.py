from django import template

register = template.Library()


@register.filter
def sub(value, arg):
    return value - arg

@register.simple_tag
def reverse_index(total_count, start_index, counter0):
    return total_count - (start_index + counter0) + 1