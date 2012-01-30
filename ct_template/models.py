""" ct_tools/ct_template/models.py

"""
from django.conf import settings
from django.db import models
from ct_groups.models import CTGroup, email_notify, add_notify_event
from ct_template.version import save_version
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from tagging.fields import TagField
from xml.etree import ElementTree as ET
import datetime

try:
    from scutils.middleware import get_current_user
except ImportError:
    from dh_django_utils.utils import get_current_user

def _encode_comment_date(d):
    return d.strftime("%Y%m%dT%H%M")

def _format_comment_date(d_str):
    """formats from string in format returned by _encode_comment_date: %Y%m%dT%H%M"""
    year = int(d_str[:4])
    month = int(d_str[4:6])
    day = int(d_str[6:8])
    hours = int(d_str[9:11])
    minutes = int(d_str[11:])
    d = datetime.datetime(year, month, day, hours, minutes)
    return d.strftime("%d/%m/%Y, %H.%M")

def format_comment_url(object_id, template_id, tView, comment_id):
    """docstring for fname"""
    # top_template_id is to direct to including template if comment has been added there.
    # really should be different for group ???
    # simplest is not to use and leave to caller to fix up = status quo
    
    # if top_template_id == '':
    #     template_id = object_id
    # else:
    #     template_id = top_template_id
    
    abs_comment_id = '%s_%s_%s' % (object_id, tView, comment_id)
    return '%stemplates/%s/%s/?tView=%s#%s' % (settings.APP_BASE, template_id, abs_comment_id, tView, abs_comment_id)

def make_template_id(obj):
    if getattr(settings, 'INCLUDE_VERSION_IN_TEMPLATE_ID', False):
        v = '_%s' % obj.version
    else:
        v = ''
    return  slugify(obj.get_metadata_text('template_id', None) or '%s%s' % (obj.label, v))
    
class ClinTemplate(models.Model):
    #name = models.CharField(max_length=64, core=True)
    #note = models.TextField()
    _template_id = models.SlugField(help_text='Do not change', max_length=64, unique=True, blank=True, null=False)
    xmlmodel = models.TextField()
    workgroup = models.ForeignKey(CTGroup)
    tags = TagField()
    is_public = models.BooleanField(blank=False, default=1)
    accept_comments = models.BooleanField(blank=False, default=1)
    accept_reviews = models.BooleanField(blank=False, default=1)
    enable_editing = models.BooleanField(blank=False, default=0)
    enable_voting = models.BooleanField(blank=False, default=0)
    included_templates = models.ManyToManyField('self', symmetrical=False, related_name='in_templates', blank=True, null=True)
    _xmlroot = None
    _metadata = _metadata_dict = None
    _inf_model = None
    _documentation = None
    _complexity_score = 0

    class Admin:
        pass
    
    class Meta:
        ordering = ['_template_id']

    def __repr__(self):
        return '%s' % self.label

    def __unicode__(self):
        return '%s' % self.label

    def get_absolute_url(self):
        return "/templates/%i/" % self.id
    
    def _get_error_model(self, err_msg):
        """docstring for _get_error_model"""
        root = ET.Element("clinicaltemplate")
        output = ET.ElementTree(root)
        
        metadata = ET.Element("metadata")
        root.append(metadata)
        n = ET.Element("item")
        n.attrib['id'] = 'm000'
        n.attrib['label'] = 'label'
        n.text = '*** Error in model xml ***'
        metadata.append(n)
        n = ET.Element("item")
        n.attrib['id'] = 'm001'
        n.attrib['label'] = 'error'
        n.text = err_msg
        metadata.append(n)
        # print ET.tostring(root)
        return output
        
    def _get_xmlroot(self):
        if self._xmlroot is None:
            try:
                self._xmlroot = ET.XML(self.xmlmodel)
            except UnicodeEncodeError, e:
                self._xmlroot = self._get_error_model(str(e))
        return self._xmlroot
    xmlroot = property(_get_xmlroot)
    
    def __getattr__(self, name):
        result = self.get_metadata_text(name)
        if result is None:
            raise AttributeError, name
        return result

    def get_metadata_text(self, key, default=None):
        """docstring for get_metadata"""
        e = self.metadata_dict.get(key, None)
        if e is None:
            # print '*** ', key, e
            return default
        else:
            # print key, e.text
            return e.text
        
    def get_workgroup(self):
        """kludge cos field should be just group to be same as other models
            TODO: change field name and update all references"""
        return self.workgroup
    group = property(get_workgroup)

    def get_item(self, item_id, name='item'):
        items = self.xmlroot.getiterator("%s%s" % (name, self.xmlns))
        item = None
        for i in items:
            if i.get("id") == item_id:
                item = i
                break
        return item

    def get_comment(self, item_id):
        return self.get_item(item_id, 'review_comment')

    def _name(self):  # just convenience, cos templates etc use name not label
        return self.label
    name = property(_name)

    def _label(self):
        return self.get_metadata_text('label', None) or self.get_metadata_text('Name', 'no label set')
    label = property(_label)

    def _version(self):
        return self.get_metadata_text('Version', '')
    version = property(_version)

    def _get_metadata(self):
        """ self.metadata is a collection of elements"""
        if self._metadata:
            return self._metadata
        self._metadata = self.xmlroot.find("%smetadata" % self.xmlns) or ET.Element("error")
        return self._metadata
    metadata = property(_get_metadata)

    def _get_metadata_dict(self):
        """ self.metadata_dict is a SortedDict with key, element.
            use get_metadata_text to get text, or self['label'] for shortcut to text"""
        if self._metadata_dict:
            return self._metadata_dict
        if not self.metadata is None:
            self._metadata_dict = SortedDict([(r.get('label'), r) for r in self.metadata.getchildren()])
        return self._metadata_dict
    metadata_dict = property(_get_metadata_dict)

    def _get_model(self):
        if self._inf_model:
            return self._inf_model
        self._inf_model = self.xmlroot.find("%smodel" % self.xmlns)
        return self._inf_model
    inf_model = property(_get_model)
    
    def _get_dataset(self):
        """returns the inf_model- used to provide alternative view"""
        return self.inf_model
    dataset = property(_get_dataset)
    
    def _get_documentation(self):
        if self._documentation:
            return self._documentation
        self._documentation = self.xmlroot.find("%sdocumentation" % self.xmlns)
        # if docs:
        #   # self._documentation = [{'content': sec.text, 'markup': sec.get('markup', ''), 'elem': sec }  for sec in docs.getchildren()]
        #   self._documentation = docs.getchildren()
        return self._documentation
    documentation = property(_get_documentation)

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
    multi_groups = property(_all_groups)
    
    def get_notify_content(self, comment=None):
        """docstring for get_notify_content"""
        id_prefix = {'i': 'form', 'd': 'docs', 'm': 'metadata'}
        if comment:
            comment = self.get_comment(comment)
            author= comment.get("author")
            content = comment.text
            item_id = comment.get("id").split(':')[0]
            url = format_comment_url(self.id, self.id, id_prefix.get(item_id[0], 0), item_id)
            
            review_date = _format_comment_date(comment.get('review_date'))          
        else:
            raise Exception('not enabled')
                    
        content = render_to_string('email_template_comment_content.txt', {
            'line_1': "The %s template has a new review comment.\n%s" % (self.name, self._used_in()),
            'line_2': '',
            'author': author, 
            'review_date':  review_date, #self.publish.strftime("%d/%m/%Y, %H.%M"),
            'content': content,
            'url': url
        })    
        return (True, content)

    def get_termbindings(self, item, new=False):
        node = item.find("%stermbindings" % self.xmlns)
        if new:
            item.remove(node)
            node = None
        if node is None:
            node = ET.Element("termbindings")
            item.append(node)
        return node

    def get_comments(self, item):
        comments = item.find("%sreview_comments" % self.xmlns)
        if comments is None:
            comments = ET.Element("review_comments")
            item.append(comments)
        return comments
        
    def add_comment(self, item_id, comment_text, user):
        import datetime
        import string
        
        comment_id = None
        
        if not self.accept_comments:
            return comment_id
        root = self.xmlroot
        item = self.get_item(item_id)
        if item != None:
            comment = ET.Element("review_comment")
            # user = utils.get_current_user()
            if user.is_anonymous():
                author = 'guest'
                comment.attrib["author_type"] = 'anonymous'
            else:
                author = user.get_full_name()
                if self.workgroup.groupmembership_set.filter(user=user.id):
                    comment.attrib["author_type"] = 'member'
                else:
                    comment.attrib["author_type"] = 'user'
            item_comments = self.get_comments(item)
            comment.attrib["author"] = author
            comment.attrib["review_date"] = _encode_comment_date(datetime.datetime.now())
            comment_id = "%s:c%s" % (item_id, len(item_comments))
            comment.attrib["id"] = comment_id
            comment.text = comment_text
            self.get_comments(item).append(comment)
            # self.xmlmodel = ET.tostring(root).replace('ns0:', '')
            # self.save()
            self.save_model()

            enabled, content = self.get_notify_content(comment=comment_id)
            # print content
            # if hasattr(group, 'multiple_groups'):
            #   all_groups = group.multiple_groups
            # else:
            #   all_groups = [group]
            
            email_notify(self.multi_groups, content, 'resource')
            add_notify_event(self, 'notify_comment', 'resource', comment_id)
            
            return comment_id


    def delete_comment(self, item_id):
        import elementtree.ElementTree as ET

        item = self.get_item(item_id)

    def reload(self, xmlmodel):
        self._xmlroot = None
        self._metadata = _metadata_dict = None
        self._inf_model = None
        self._documentation = None
        self._complexity_score = 0
        self.xmlmodel = xmlmodel
    
    def save_model(self):
        if self.get_metadata_text('error') is None:
            self.xmlmodel = ET.tostring(self.xmlroot).replace('ns0:', '')
            self.save()
        
    def save(self, *args, **kwargs):
        self._xmlroot = self._metadata = self._inf_model = self._documentation = None
        template_id = kwargs.pop('template_id', None)
        self._template_id = template_id or make_template_id(self)
        super(ClinTemplate, self).save()
    
    def set_termbindings_from_txt(self, parent, txt):
        tbs = self.get_termbindings(parent, new=True)
        for dc in [t for t in txt.split('\r\n') if t]:
            tb = ET.Element("termbinding", {})
            tb.text = dc
            tbs.append(tb)


from django.db.models.signals import post_delete, post_save

def version_delete(sender, **kwargs):
    pass

def version_save(sender, **kwargs):
    instance = kwargs['instance']
    fn = '%s%05d_%s.xml' % (settings.CT_VERSION_PATH, instance.id, instance._template_id)
    save_version(fn, instance.xmlmodel)
    
if settings.CT_VERSION_SAVES:
    # post_delete.connect(version_delete, dispatch_uid="ct_version")
    post_save.connect(version_save, sender=ClinTemplate, dispatch_uid="ct_version")

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

    def _group(self):
        return self.template.workgroup
    group = property(_group)

    def get_notify_content(self, comment=None):
        """docstring for get_notify_content"""
    
        line_1 = _('A review has been added to: %s.') % self.template.label
        author= self.reviewer.get_full_name()
        content = '%s: %s\n%s' % (ugettext('Rating'), self.rating, self.review)
        url = '%s%s#reviews' % ( settings.APP_BASE[:-1], self.template.get_absolute_url())
                
        content = render_to_string('email_template_comment_content.txt', {
            'line_1': line_1,
            'line_2': '',
            'author': author, 
            'review_date': self.review_date.strftime("%d/%m/%Y, %H.%M"),
            'content': content,
            'url': url
        })    
        return (True, content)


def notify_new_review(sender, instance, **kwargs):
    if kwargs.get('created', False):
        enabled, content = instance.get_notify_content()
        email_notify([instance.template.workgroup], content, 'resource')
        add_notify_event(instance, 'notify', 'resource')

# if not settings.DEBUG:
post_save.connect(notify_new_review, sender=ClinTemplateReview)



