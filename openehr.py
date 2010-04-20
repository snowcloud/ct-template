import elementtree.ElementTree as ET

# path='/Users/derek/dev_django/ct_tools/ct_template/openehr_test/'
path='/Users/derek/Dropbox/S-R Modelling/templates/composition/'
# path='/Users/derek/Dropbox/S-R Modelling/other-templates/'
fname='Cardiology opinion Report.opt'
# fname='SR_WEHR Liver Transplant Pre-operative workup summary.opt'
# fname='NEHTA Lymphoma Synoptic Report Framework.opt'

xsi="{http://www.w3.org/2001/XMLSchema-instance}"
nsp="{http://schemas.openehr.org/v1}"

# NB attribs only need namespace if specified in file
#  eg  "xsi:type=..." does, but "code=..." doesn't

GROUP_RM_TYPE_NAMES = ('EVENT_CONTEXT', 'SECTION', 'CLUSTER', 'OBSERVATION', 'EVALUATION')
ITEM_RM_TYPE_NAMES = ('ELEMENT',)
ITEM_VALUETYPES = (
    'DV_TEXT', 'DV_DATE_TIME', 'DV_DATE', 'DV_CODED_TEXT', 'DV_DURATION', 'DV_QUANTITY',
    'DV_MULTIMEDIA', 'DV_BOOLEAN', 'DV_ORDINAL', 'DV_COUNT', 'DV_EHR_URI', 'DV_PROPORTION'
     ) 
ITEM_VALUETYPE_UNDEFINED = 'not_defined'
IGNORE_ATTRIBUTES = ('protocol',)
IGNORE_CHILDREN_TYPE = ('ARCHETYPE_SLOT',)

def ns(path):
    """utility function to put namespace in for tags e.g. {http://schemas.openehr.org/v1}tag"""
    
    if path[-1] == '/':
        path = path[:-1]
    if path.startswith('.//'):
        result = path.replace('.//', './/%s' % nsp)
    else:
        result = '%s%s' % (nsp, path.replace('/', '/%s' % nsp))
    # print result
    return result
    
# run with cmd-R

def _findname(el):
    """docstring for _findname"""
    return el.findtext(ns('.//list')) or '-'

def get_term_defs(node):
    """docstring for _get_term_defs"""
    result = {}
    for d in node.findall(ns('term_definitions')):
        for t in d.findall(ns('items')): 
            if t.get("id") == 'text':
                # print t.text
                result[d.get('code')] = t.text
    return result
    
    
    
class OptProcessor(object):
    """docstring for OptProcessor"""
    def __init__(self, attrs= {}, note=''):
        super(OptProcessor, self).__init__()
        self.root = ET.Element("clinicaltemplate", attrs)
        n = ET.Element("note")
        n.text = note
        self.root.append(n)
        self.output = ET.ElementTree(self.root)
        self.id = 0
        
    def dump_output(self):
        """docstring for dump_output"""
        print ET.tostring(self.root)
        # ET.dump(self.output)
        

    def _add_item_attribs(self, el, attribs):
        """docstring for fname"""
        
        if 'tag' in attribs:
            tag = ET.Element(attribs['tag'])
            el.append(tag)
            if 'text' in attribs:
                tag.text = attribs['text']
            if 'children' in attribs:
                for c in attribs['children']:
                    self._add_item_attribs(tag, c)
        
        # item_attrs = node_info.get('item_attrs', {})
        # if item_attrs.get('valueset', None):
        #     vs = ET.Element("valueset")
        #     for code in item_attrs['valueset']:
        #         v = ET.Element("value")
        #         v.text = code
        #         vs.append(v)
        #     to_node.append(vs)
        # TODO  try to get DV funcs to fill attribs and just write the dict into item
        #       maybe should be using child elements for all other than basic?

    
    
    def process_me(self, to_node, node_info):
        """read node_info and-
        if a group or control, add child to to_node in output tree, fill and return child
        else return to_node
        """
        if to_node is None:
            to_node = self.root
        
        if node_info.get('rm_attribute_name', None) == 'name':
            to_node.attrib['label'] = node_info.get('label', '')
            
        if node_info.get('valueType', None):
            attrs = { 'id': 'i%04d' % self.id, 'label': node_info.get('label', '-'), 'valueType': node_info['valueType'] }
            el = ET.Element("item", attrs)
            to_node.append(el)
            to_node = el
            self.id += 1
            for attribs in node_info.get('item_attrs', []):
                self._add_item_attribs(el, attribs)
        
        return to_node, node_info['term_defs']

def DV_DEFAULT(node, term_defs):
    """default handler for DV_*"""
    return []


def DV_CODED_TEXT(node, term_defs):
    """docstring for DV_CODED_TEXT"""
    result = []
    # TODO only finding terminology_id == local
    # terminology_id = node.findtext(ns('.//value'))
    # terminology_id = node.findtext(ns('attributes/rm_attribute_name'))
    terminology_id = node.findtext(ns('attributes/children/attributes/children/terminology_id/value'))
    code_list = node.findall(ns('attributes/children/attributes/children/code_list'))
    result.append({'tag': 'terminology_id', 'text': terminology_id})
    result.append({'tag': 'valueset', 'children': [{'tag': 'value', 'text': term_defs.get(c.text, 'unknown code')} for c in code_list]})
    return result

    """
    <children xsi:type="C_COMPLEX_OBJECT">
      <rm_type_name>DV_CODED_TEXT</rm_type_name>
      <occurrences>
        <lower_included>true</lower_included>
        <upper_included>true</upper_included>
        <lower_unbounded>false</lower_unbounded>
        <upper_unbounded>false</upper_unbounded>
        <lower>1</lower>
        <upper>1</upper>
      </occurrences>
      <node_id />
      <attributes xsi:type="C_SINGLE_ATTRIBUTE">
        <rm_attribute_name>defining_code</rm_attribute_name>
        <existence>
          <lower_included>true</lower_included>
          <upper_included>true</upper_included>
          <lower_unbounded>false</lower_unbounded>
          <upper_unbounded>false</upper_unbounded>
          <lower>1</lower>
          <upper>1</upper>
        </existence>
        <children xsi:type="CONSTRAINT_REF">
          <rm_type_name>CODE_PHRASE</rm_type_name>
          <occurrences>
            <lower_included>true</lower_included>
            <upper_included>true</upper_included>
            <lower_unbounded>false</lower_unbounded>
            <upper_unbounded>false</upper_unbounded>
            <lower>1</lower>
            <upper>1</upper>
          </occurrences>
          <node_id />
          <reference>ac0.1</reference>
        </children>
      </attributes>
    </children>
    """

def DV_QUANTITY(node, term_defs):
    """docstring for DV_QUANTITY"""
    # using 'units' below was failing in Elementtree -reserved word?
    result = [{'tag': 'qunits', 'text': node.findtext(ns('attributes/children/list/units'))}]
    # result.setdefault('attributes', {})['units'] = node.findtext(ns('attributes/children/list/units'))
    # print result
    return result


def _get_item_attrs(node, term_defs):
    """docstring for _get_item_attrs"""

    vtype = node.findtext(ns('attributes/children/rm_type_name'))
    if vtype in ITEM_VALUETYPES:
        func = globals().get(vtype, DV_DEFAULT)
        return vtype, func(node, term_defs)
    else:
        print 'unrecognised valuetype: %s in %s' % (vtype, node)
        return ITEM_VALUETYPE_UNDEFINED, {}

def get_node_info(node, term_defs):
    """inspects opt node, and returns dict of info for processing"""
    node_info = {}
    
    subnodes = list(node.findall(ns('children')))
    if len(subnodes) == 0:
         subnodes = list(node.findall(ns('attributes')))
    node_info['subnodes'] = subnodes
    node_info['tag'] = node.tag[len(nsp):] # strips schema prefix
    node_info['type'] = node.get('%stype' % xsi)
    
    # it's a child node
    if node_info['tag'] == 'children':
        node_info['rm_type_name'] = node.findtext(ns('rm_type_name'))
        new_term_defs = get_term_defs(node)
        if len(new_term_defs) > 0:
            term_defs = new_term_defs
        term_def = node.findtext(ns('node_id'))
        node_info['label'] = term_defs.get(term_def, '')

        if ((node_info.get('rm_type_name', None) in GROUP_RM_TYPE_NAMES) and
            (node_info.get('type', None) not in IGNORE_CHILDREN_TYPE)):
            node_info['valueType'] = 'group'
        elif node_info.get('rm_type_name', None) in ITEM_RM_TYPE_NAMES:
            node_info['valueType'], node_info['item_attrs'] = _get_item_attrs(node, term_defs)

    # it's an attribute node
    elif node_info['tag'] == 'attributes':
        node_info['rm_attribute_name'] = node.findtext(ns('rm_attribute_name'))
        if node_info['rm_attribute_name'] == 'name':
            node_info['label'] = _findname(node)
        elif node_info['rm_attribute_name'] in IGNORE_ATTRIBUTES:
            # go no further down this branch
            node_info['subnodes'] = []
            
    # use attr name as default if no name found
    # should only be needed on context/other_context
    if node_info.get('label', None) == '':
        node_info['label'] = node.findtext(ns('attributes/rm_attribute_name'))
    node_info['term_defs'] = term_defs
    return node_info
    
def process_opt(processor, to_node, term_defs, opt_element):
    """
    recursive descent parsing of opt_element.
    passes element to processor
    processor returns current node in output tree for element to be added to
    """
    node_info = get_node_info(opt_element, term_defs)
    next_node, term_defs = processor.process_me(to_node, node_info)
    for n in node_info['subnodes']:
        process_opt(processor, next_node, term_defs, n)


###############################################################

tree = ET.parse("%s%s" % (path, fname))
template_id = tree.findtext(ns('template_id/value'))
concept = tree.findtext(ns('concept'))

template_attrs = {
    'template_id': template_id, 'label': concept,
    'version': "0.1", 'status': "draft", 'source': "",
    'xmlns': 'http://schemas.clinicaltemplates.org/v2'
    }
note = "some descriptive text here..."
processor = OptProcessor(template_attrs, note)


root = tree.find(ns('definition'))
term_defs = get_term_defs(root)
process_opt(processor, None, term_defs, root)

processor.dump_output()







# ins=attrins='. '
# 
# class OptAttribute(object):
#     """docstring for OptAttribute"""
#     def __init__(self, element, term_defs= {}):
#         super(OptAttribute, self).__init__()
#         self.element = element
#         self.term_defs = term_defs
#         self.name = None
#         self.build()
# 
#     def __repr__(self):
#         """docstring for __repr__"""
#         return '%s: %s' % ((self.name or self.rm_attribute_name), self.type)
# 
#     def dump(self, indent=0, limit=None):
#         """docstring for dump"""
#         result = ['%s%s' % (attrins, str(self))]
#         if not limit or limit > indent:
#             for a in self.children:
#                 result.append('%s%s' % (indent * attrins, a.dump(indent+1, limit)))
#         return '\n'.join(result)        
#         
#     def build(self):
#         """docstring for build"""
#         self.rm_attribute_name = self.element.findtext(ns('rm_attribute_name'))
#         self.type = self.element.get('%stype' % xsi)
#         self.children = []
#         if self.rm_attribute_name not in ('name', 'protocol'):
#             for c in self.element.findall(ns('children')):
#                 e = OptChild(c, self.term_defs)
#                 self.children.append(e)
#         elif self.rm_attribute_name == 'name':
#             self.name = _findname(self.element)
#         
#         
# class OptChild(object):
#     """docstring for OptChild"""
#     def __init__(self, element, term_defs={}):
#         super(OptChild, self).__init__()
#         self.element = element
#         self.term_defs = term_defs
#         self.build()
# 
#     def __repr__(self):
#         """docstring for __repr__"""
#         return '%s (%s: %s)' % (self.term_def, self.rm_type_name, self.type)
#         
#     def build(self):
#         """docstring for build"""
#         self.rm_type_name = self.element.findtext(ns('rm_type_name'))
#         self.type = self.element.get('%stype' % xsi)
#         self.attributes= []
#         new_term_defs = {}
#         for d in self.element.findall(ns('term_definitions')):
#             for t in d.findall(ns('items')): 
#                 if t.get("id") == 'text':
#                     # print t.text
#                     new_term_defs[d.get('code')] = t.text
#         if len(new_term_defs) > 0:
#             self.term_defs = new_term_defs
#         term_def = self.element.findtext(ns('node_id'))
#         self.term_def = self.term_defs.get(term_def, '')
#         for c in self.element.findall(ns('attributes')):
#             e = OptAttribute(c, self.term_defs)
#             self.attributes.append(e)
#         
#     def dump(self, indent=0, limit=None):
#         """docstring for dump"""
#         result = ['%s%s' % (ins, str(self))]
#         if not limit or limit > indent:
#             for a in self.attributes:
#                 result.append('%s%s' % (indent * ins, a.dump(indent+1, limit)))
#         # result.append('%s%s' % (ins, str(self.term_defs)))
#         return '\n'.join(result)        
#         
# class OptTemplate(object):
#     """a clinical template object derived from an openEHR opt file"""
#     def __init__(self, path, fname):
#         super(OptTemplate, self).__init__()
#         self.path, self.fname = path, fname
#         self.tree = ET.parse("%s%s" % (path, fname))
#         self.concept = self.tree.findtext(ns('concept'))
#         self.build()
#         
#     def __repr__(self):
#         """docstring for test"""
#         result = self.concept
#         return result
# 
#     def build(self):
#         """parses opt xml tree to build OptTemplate nodes"""
#         self.root = OptChild(self.tree.find(ns('definition')))
# 
#     def test(self, limit=None):
#         """docstring for test"""
#         return self.root.dump(0, limit)
#         
# t = OptTemplate(path, fname)
# # print t
# print t.test()

# print '========\ndone'


# do a helper function to get dict of terms
#   fetch term_definitions, get @code and read text for each item @text, @description
# <term_definitions code="at0000">
#     <items id="text">Report</items>
#     <items id="description">Generic reporting composition in response to a request for
#         information or testing</items>
# </term_definitions>

# 4 sections
# template/definition/attributes / content / children/attributes/children x 4

# ECG REcording - 12-lead standard
# Echocardiography
# Dobutamine stress echo test
# Cardiology evaluation




# print tree.findtext(ns('definition/archetype_id/value'))
# terms = tree.findall(ns('definition/term_definitions'))
# 
# for t in terms:
#     print t.get("code")
#     



# at0000


