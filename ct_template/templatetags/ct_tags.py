from django.conf import settings
from django import template
from django.utils.translation import ugettext as _

register = template.Library()

from ct_template.models import ClinTemplate
from ct_template.templatetags.eltree import get_template
from ct_groups.templatetags.ct_groups_tags import group_edit

@register.filter
def rating_display(value):
    return 'rating- %d' % value

# @register.filter
# def synonym(value):
#     v = getattr(settings, 'SYNONYMS', {})
#     return _(v.get(value, value))

@register.inclusion_tag('tree_node_detail.html')
def add_node_to_tree(item, top_template_id, template):
    if not isinstance (template, ClinTemplate):
        template = get_template(elattrib(template, 'include'))
    return {
        'elem': item,
        'top_template_id': top_template_id,
        'template': template
    }

@register.filter
def show_data_view(template, user):
    return template.show_data_view == 'show' or (template.show_data_view == 'editors_only' and group_edit(template.workgroup, user))
    