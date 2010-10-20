from django import template
from django.utils.translation import ugettext as _


register = template.Library()

# try:
from django.conf import settings


@register.filter
def rating_display(value):
    return 'rating- %d' % value

@register.filter
def site_resource_name(value):
    v = getattr(settings, 'SYNONYMS', {})
    return _(v.get(value, value))
