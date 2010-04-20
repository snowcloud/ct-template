from django import template


register = template.Library()


@register.filter
def rating_display(value):
	return 'rating- %d' % value
