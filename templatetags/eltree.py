from django import template
from django.contrib.markup.templatetags.markup import textile
from django.template.defaultfilters import safe
from django.utils.safestring import mark_safe
from xml.etree import ElementTree as Elem
import time
import datetime
from ct_template.models import ClinTemplate
from django.shortcuts import get_object_or_404
from django.http import Http404

register = template.Library()

# TODO can this go in settings?
#	   should be dynamic, read from xml
#	   would need a context variable passed in with all tags

# nsp = '{http://schemas.clinicaltemplates.org/v2}'

def ns(path, nsp):
	"""utility function to put namespace in for tags e.g. {http://schemas.openehr.org/v1}tag"""
	if path[-1] == '/':
		path = path[:-1]
	if path.startswith('.//'):
		result = path.replace('.//', './/%s' % nsp)
	else:
		result = '%s%s' % (nsp, path.replace('/', '/%s' % nsp))
	return result

@register.filter
def elattrib(value, arg):
	#v = value.get(arg, "")
	if (arg.find("_date") > -1):
		# The easiest way to convert this to a datetime seems to be; 
		EpochSeconds = time.mktime(time.strptime(value.get(arg, "00000000T0000"), "%Y%m%dT%H%M")) 
		d = datetime.datetime.fromtimestamp(EpochSeconds)	
		return d
	else:
		return value.get(arg, "")

@register.filter
def items_for_view(t, view):
	views = ('inf_model', 'inf_model', 'documentation', 'metadata')
	return getattr(t, views[int(view)])

@register.filter
def items(value, nsp):
	if value is None: return ""
	v = value.findall(ns("item", nsp))
	if v is None: return ""
	else: return v

@register.filter
def doc_content(value):
	"""docstring for markup"""
	content = value.text
	m = value.get('markup', None)
	if m == 'textile':
		return textile(content)
	else:
		return mark_safe(content)

@register.filter
def fixedtext(value):
	return elattrib(value, 'valueType') == 'fixedtext'

def _get_template(id):
	try:
		return	get_object_or_404(ClinTemplate, _template_id__exact=id)
	except Http404:
		pass
	return None
	
@register.filter
def includes_template(value):
	return elattrib(value, 'valueType') == 'include_template'

@register.filter
def included_template_name(value):
	if not includes_template(value):
		return ''
	# should have a template then...
	clin_template = included_template(value)
	if clin_template is None:
		return 'NOT FOUND'
	else:
		return clin_template.name
	
@register.filter
def included_template(value):
	if not includes_template(value):
		return None
	return _get_template(elattrib(value, 'include'))

@register.filter
def included_template_items(value, nsp):
	clin_template = included_template(value)
	if clin_template is None:
		return None
	else:
		return items(clin_template.xmlroot, nsp)

def _get_shared_values(share_id, template):
	vs = None
	for e in template.inf_model.findall(ns('shared_valueset', template.xmlns)):
		if e.attrib['id'] == share_id:
			vs = e
			break
	return vs

@register.filter
def values(value, template):
	v = value.find(ns("valueset", template.xmlns))
	if v is None:
		return None
	share_id = elattrib(v, 'share_id')
	if share_id == '':
		return v
	else:
		return _get_shared_values(share_id, template)

@register.filter
def review_comments(value, nsp):
	c = value.find(ns("review_comments", nsp))
	if c is None:
		return ""
	v = c.findall(ns("review_comment", nsp))
	if v is None:
		return ""
	else:
		return v

@register.inclusion_tag('item_editor_menu.html')
def item_editor(item):
	"""docstring for item_editor"""
	return {
		'elem': item,
	}

@register.inclusion_tag('item_detail.html')
def item_display(item, top_template_id, template, level=0, tView=None, user=None):
	if not isinstance (template, ClinTemplate):
		template = _get_template(elattrib(template, 'include'))
	return {
		'elem': item,
		'top_template_id': top_template_id,
		'template': template,
		'this_level': level,
		'child_level': level + 1,
		'tView': tView,
		'user': user
	}

from django.template import Context, loader, TemplateDoesNotExist

@register.simple_tag
def item_display_widget(item, template):
	datatype = elattrib(item, "valueType")
	widget = elattrib(item, "widget")
	if widget == '': # no widget specified, so get default
		templates = {
			'date': 'date', 
			'datetime': 'datetime',
			'duration_secs': 'integer',
			'duration_mins': 'integer',
			'duration_hours': 'integer',
			'fixedtext': 'fixedtext', 
			'freetext': 'freetext',
			'frequency_mins': 'integer',
			'frequency_hours': 'integer',
			'group': 'group',
			'include_template': 'include_template', 
			'integer': 'integer',
			'not_defined': 'not_defined', 
			'percent': 'integer', 
			'size_cm': 'integer', 
			'radioset': 'radioset',
			'text': 'textline',
			'yes_no': 'radioset_yn', 
			'yes_no_dk': 'radioset_yndk', 
			'yes_no_na': 'radioset_ynna', 
			'nominal_list': 'select', 
			'ordinal_list': 'select',
			'DV_BOOLEAN': 'textline',
			'DV_CODED_TEXT': 'select',
			'DV_COUNT': 'textline',
			'DV_DATE': 'date',
			'DV_DATE_TIME': 'datetime',
			'DV_DURATION': 'textline',
			'DV_EHR_URI': 'textline',
			'DV_MULTIMEDIA': 'textline',
			'DV_ORDINAL': 'select',
			'DV_PROPORTION': 'textline',
			'DV_QUANTITY': 'integer',
			'DV_TEXT': 'textline',			  
		}
		if datatype in templates:
			widget = templates[datatype]
		else:
			widget = 'error'
	
		if datatype.find('list') > -1:
			if elattrib(item, "select") == 'multi_select':
				widget = 'multi_select'
			else:
				v = values(item, template)
				if v and (len(v) < 7):
					widget = 'radioset'

	fixes = { 
		'percent': '%', 'size_cm': 'cm', 
		'duration_secs': 'secs', 'duration_mins': 'mins', 'duration_hours': 'hours', 
		'frequency_secs': 'secs', 'frequency_mins': 'mins', 'frequency_hours': 'hours'
		}
	if datatype in fixes:
		suffix = fixes[datatype]
	else:
		units = item.findtext(ns('qunits', template.xmlns))
		if units:
			suffix = units
		else:
			suffix = ''
	
	c = Context({ 'elem': item, 'suffix': suffix, 'template': template })
	
	try:
		t_loaded = loader.get_template('item_widget_%s.html' % widget)	
		return t_loaded.render(c)
	except TemplateDoesNotExist:
		return '<div class="ct_widget">[ERROR: TEMPLATE NOT FOUND]</div>'
	

