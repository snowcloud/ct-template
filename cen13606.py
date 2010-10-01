import elementtree.ElementTree as ET

# <archetype xmlns:at="openEHR/v1/Archetype" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

at="{openEHR/v1/Archetype}"
xsi="{http://www.w3.org/2001/XMLSchema-instance}"
nsp=""

GROUP_RM_TYPE_NAMES = ('EVENT_CONTEXT', 'SECTION', 'CLUSTER', 'OBSERVATION', 'EVALUATION')
ITEM_RM_TYPE_NAMES = ('ELEMENT',)
ITEM_VALUETYPES = (
    # 'DV_TEXT', 'DV_DATE_TIME', 'DV_DATE', 'DV_CODED_TEXT', 'DV_DURATION', 'DV_QUANTITY',
    # 'DV_MULTIMEDIA', 'DV_BOOLEAN', 'DV_ORDINAL', 'DV_COUNT', 'DV_EHR_URI', 'DV_PROPORTION',
    'PQ', 'SIMPLE_TEXT', 
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

def _get_item_attrs(node, term_defs):
    """docstring for _get_item_attrs"""

    vtype = node.findtext(ns('attributes/children/rm_type_name'))
    if vtype in ITEM_VALUETYPES:
        print vtype
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

def get_term_defs(node, lang='en-gb'):
    """docstring for _get_term_defs"""
    result = {}
    for term_definitions in node.findall(ns('term_definitions')):
        ont_lang = term_definitions.find(ns('language'))
        if (ont_lang is not None) and ont_lang.text == lang:
            for terms in term_definitions.findall(ns('terms')):
                code = terms.find(ns('code')).text
                for item in terms.findall(ns('items//item')):
                    if item.find(ns('key')).text == 'text':
                        result[code] = item.find(ns('value')).text
    return result
    
def process_model(processor, to_node, opt_element, term_defs):
    """
    recursive descent parsing of opt_element.
    passes element to processor
    processor returns current node in output tree for element to be added to
    """
    node_info = get_node_info(opt_element, term_defs)
    next_node, term_defs = processor.process_model_node(to_node, node_info)
    for n in node_info['subnodes']:
        process_model(processor, next_node, n, term_defs)

class ArchProcessor(object):
    """docstring for ArchProcessor"""
    def __init__(self, tree, attrs= {}):
        super(ArchProcessor, self).__init__()
        
        self.source_tree = tree
        self.source_root = tree.find(ns('definition'))
        self.source_ontology = tree.find(ns('ontology'))
        self.root = ET.Element("clinicaltemplate", attrs)
        self.model = ET.Element("model")
        self.root.append(self.model)
        self.output = ET.ElementTree(self.root)
        self.id = 0
        
    def dump_output(self):
        """docstring for dump_output"""
        self._write_metadata_to_output()
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

    
    def get_metadata(self, term_defs):
        """docstring for self._get_metadata"""
        result = {}
        # for m in node.findall(ns("TaggedValue")):
        #     result.setdefault(strip_tag(m.attrib['tag']), []).append(m.attrib.get('value', '-'))
        # for k, v in result.items():
        #     result[k] = ' | '.join(v)
        result['template_id'] = self.source_tree.findtext(ns('archetype_id'))
        result['label'] = term_defs.get(self.source_tree.findtext(ns('concept_code')), 'label-not-set')
        self.metadata = result
        
    def _write_metadata_to_output(self):
        output = ET.Element("metadata")
        self.root.append(output)
        
        self.item_id = 10
        for k, v in self.metadata.items():
            # <item id="m010" label="label">My second DCM</item>
            attrs = { 'id': 'm%04d' % self.item_id, 'label': k }
            n = ET.Element("item", attrs)
            n.text = v
            self.item_id += 10
            output.append(n)
        self.item_id = 0


    def process_model_node(self, to_node, node_info):
        """read node_info and-
        if a group or control, add child to to_node in output tree, fill and return child
        else return to_node
        """
        if to_node is None:
            to_node = self.model
        
        if node_info.get('rm_attribute_name', None) == 'name':
            to_node.attrib['label'] = node_info.get('label', '')
            
        if node_info.get('valueType', None):
            attrs = { 'id': 'i%04d' % self.id, 'label': node_info.get('label', '-'), 'valueType': node_info['valueType'] }
            el = ET.Element("item", attrs)
            to_node.append(el)
            to_node = el
            self.id += 10
            for attribs in node_info.get('item_attrs', []):
                self._add_item_attribs(el, attribs)
        
        return to_node, node_info['term_defs']
    
def DV_DEFAULT(node, term_defs):
    """default handler for DV_*"""
    return []




