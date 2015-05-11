from django import template

register = template.Library()


@register.filter
def durations(value):
    seconds = int(value)
    hours = seconds / 3600
    minutes = (hours % 3600) / 60
    seconds = (hours % 3600) % 60

    return "{} hours, {} minutes, {} seconds".format(hours, minutes, seconds)
