""" ct_tools/ct_template/models.py

"""
from django.db import models
from ct_groups.models import CTGroup, email_notify, add_notify_event
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from dh_django_utils import utils
from django.conf import settings
from django.utils.datastructures import SortedDict
from tagging.fields import TagField
from xml.etree import ElementTree as ET
import datetime


class ClinTemplate(models.Model):
	#name = models.CharField(max_length=64, core=True)
	#note = models.TextField()
	_template_id = models.SlugField(max_length=64, unique=True, blank=True, null=False)
	xmlmodel = models.TextField()
	workgroup = models.ForeignKey(CTGroup)
	tags = TagField()
	is_public = models.BooleanField(blank=False, default=1)
	accept_comments = models.BooleanField(blank=False, default=1)
	accept_reviews = models.BooleanField(blank=False, default=1)
	included_templates = models.ManyToManyField('self', symmetrical=False, related_name='in_templates', blank=True, null=True)
	_xmlroot = None
	_metadata = None
	_complexity_score = 0

	class Admin:
		pass

	def __repr__(self):
		return '%s' % self.metadata.get('label', 'no label set')

	def __unicode__(self):
		return '%s' % self.metadata.get('label', 'no label set')

	def get_absolute_url(self):
		return "/templates/%i/" % self.id
	
	def _get_xmlroot(self):
		if self._xmlroot is None:
			self._xmlroot = ET.XML(self.xmlmodel)
		return self._xmlroot
	xmlroot = property(_get_xmlroot)
	
	def __getattr__(self, name):
		try:
			return self.metadata[name]
		except KeyError:
			raise AttributeError, name

	def get_item(self, item_id, root):
		items = root.getiterator("%sitem" % self.xmlns)
		item = None
		for i in items:
			if i.get("id") == item_id:
				item = i
				break
		return item
	
	def _name(self):  # just convenience, cos templates etc use name not label
		return self.label
	name = property(_name)

	def _label(self):
		return self.metadata.get('label', 'no label set')
	label = property(_label)

	def get_metadata(self):
		if self._metadata:
			return self._metadata
		# {'gub': 'jings', 'frud': 'kludge'}
		self._metadata = SortedDict()
		items = self.xmlroot.find("%smetadata" % self.xmlns)
		if items is None:
			return {}
		result = [(r.tag, r.text) for r in items.getchildren() if not r.tag.startswith('_')]
		self._metadata = SortedDict(result)
		return self._metadata
	metadata = property(get_metadata)

	def _xmlns(self):
		"""reads xmlns attribute of root, returns as string if present, otherwise empty string"""
		start = self.xmlmodel.find('xmlns=')
		if start == -1:
			return ''
		end = self.xmlmodel.find('>')
		return'{%s}' % self.xmlmodel[start+7:end-1]
	xmlns = property(_xmlns)
	
	def _used_in(self):
		results = [t.name for t in self.in_templates.all()]
		if len(results) == 0:
			return ''
		return 'This template is also used in: %s' % ', '.join(results)
	
	def _all_groups(self):
		result = set([template.workgroup for template in self.in_templates.all()])
		result.add(self.workgroup)
		return result
	
	# def _email_notify(self, content):
	#	  import string
	#	  from django.core.mail import EmailMessage
	# 
	#	  t = string.Template(settings.EMAIL_REVIEW_BODY_TEMPLATE)
	#	  body = t.safe_substitute(content= content, dummy= datetime.datetime.now().strftime("%H:%M"))
	#	  all_memberships = []
	#	  for group in self._all_groups():
	#		  all_memberships.extend(group.groupmembership_set.all())
	#	  add_list = list(frozenset([member.user.email for member in all_memberships if member.notify_tool_updates]))
	#	  if len(add_list) > 0:
	#		  email = EmailMessage(
	#			  '[clintemplate] %s update' % self.workgroup.name, 
	#			  body, 
	#			  'do not reply <do_not_reply@clintemplate.org>',
	#			  ['do_not_reply@clintemplate.org'],
	#			  add_list
	#		  )
	#		  email.send()

	def get_comments(self, item):
		comments = item.find("%sreview_comments" % self.xmlns)
		if comments is None:
			comments = ET.Element("review_comments")
			item.append(comments)
		return comments
		
	def add_comment(self, item_id, comment_text):
		import datetime
		import string
		
		if not self.accept_comments:
			return
		root = self.xmlroot
		item = self.get_item(item_id, root)
		if item != None:
			comment = ET.Element("review_comment")
			user = utils.get_current_user()
			if user.is_anonymous():
				author = 'guest'
				comment.attrib["author_type"] = 'anonymous'
			else:
				author = user.get_full_name()
				if self.workgroup.groupmembership_set.filter(user=user.id):
					comment.attrib["author_type"] = 'member'
				else:
					comment.attrib["author_type"] = 'user'
			comment.attrib["author"] = author
			comment.attrib["review_date"] = datetime.datetime.now().strftime("%Y%m%dT%H%M")
			comment.text = comment_text
			self.get_comments(item).append(comment)
			self.xmlmodel = ET.tostring(root).replace('ns0:', '')
			#<review_comment author="derek" review_date="20060410T2130"> bollocks. </review_comment>
			
			t=string.Template(settings.EMAIL_REVIEW_CONTENT_TEMPLATE)
			item_ref = '%s_%s' % (self.id, item_id)
			# content = t.safe_substitute(
			#	  line_1= "The %s template has been updated.\n%s\n" % (self.name, self._used_in()),
			#	  line_2= "Data item '%s' has a new review comment." % item.attrib["label"],
			#	  author= author, 
			#	  review_date= datetime.datetime.now().strftime("%d/%m/%Y, %H.%M"), comment= comment_text,
			#	  url= '%stemplates/%i/%s/#%s' % ( settings.APP_BASE, self.id, item_ref, item_ref),
			#	  )
			# self._email_notify(content)
			self.save()

			enabled, content = self.get_notify_content(comment=instance)
			email_notify(obj.group, content, 'blog')
			add_notify_event(obj, 'notify_comment', 'blog', instance.id)



	def delete_comment(self, item_id):
		import elementtree.ElementTree as ET

		item = self.get_item(item_id)

	def save(self):
		self._xmlroot = self._metadata = None
		self._template_id = slugify(self.metadata.get('template_id', 'template id not set'))
		super(ClinTemplate, self).save()

from dh_django_utils import utils

class ClinTemplateReview(models.Model):
	reviewer = models.ForeignKey(User)
	review_date = models.DateTimeField(default=datetime.datetime.now(), blank=False, null=True)
	rating = models.SmallIntegerField(blank=False)
	#rating = models.ChoiceField(choices=[('1', '1'), ('2', '2')], blank=False)
	review = models.TextField(blank=False)
	template = models.ForeignKey(ClinTemplate, blank=False, null=True)
	is_public = models.BooleanField(blank=False, default=1)
	
	class Admin:
		pass

	class Meta:
		ordering = ['review_date']

	def __repr__(self):
		return '%s - %s' % (self.template, self.reviewer)

	def __unicode__(self):
		return '%s - %s' % (self.template, self.reviewer)

	def save(self):
		if self.reviewer_id is None:
			self.reviewer_id = utils.get_current_user().id
		super(ClinTemplateReview, self).save()
	