from django.template.defaultfilters import slugify
import elementtree.ElementTree as ET


UML = "{omg.org/UML1.3}"
# DOC_HEADINGS = ('',)

VALUETYPES = {
    'data': 'integer',
    'container': 'group',
    }

"""
XMI.content
    UML:Model
        UML:Namespace.ownedElement
            UML:Package name="Information Model"
                UML:Namespace.ownedElement
            
                    ###############################################################
                    UML:Class name="BradenScale"
                        xmi.id="EAID_78701929_8194_418c_A1AF_12F454CA06E8"
                        UML:ModelElement.stereotype
                            UML:Stereotype name="rootconcept"
                    ###############################################################
                    UML:Class name="Items"
                        <UML:ModelElement.stereotype>
                            <UML:Stereotype name="container"
                    ###############################################################
                    UML:Class name="Activity"
                        UML:ModelElement.stereotype
                            UML:Stereotype name="data"
                        UML:Classifier.feature>
                            UML:Attribute name="Bedfast"
                            UML:Attribute name="Chairfast"
                            UML:Attribute name="Walks frequently"
                            UML:Attribute name="Walks occasionally"
                    ###############################################################
                    UML:Association
                        ModelElement.taggedValue
                            TaggedValue tag="ea_type" value="Aggregation"
                            TaggedValue tag="direction" value="Source -&gt; Destination"/>
                            TaggedValue tag="seqno" value="0"/>
                            TaggedValue tag="ea_localid" value="115"/>
                            TaggedValue tag="ea_sourceName" value="WearsShoes"/>
                            TaggedValue tag="ea_targetName" value="BodyWeight"
                            TaggedValue tag="ea_sourceType" value="Class"
                            TaggedValue tag="ea_targetType" value="Class"
                            TaggedValue tag="ea_sourceID" value="375"
                            TaggedValue tag="ea_targetID" value="374"
                            TaggedValue tag="lb" value="0..



Activity xmi.id="EAID_17C366D0_7119_45ac_A1AC_794964373E42"

UML:Generalization
    subtype="EAID_17C366D0_7119_45ac_A1AC_794964373E42"
    supertype="EAID_182100FB_449C_483f_923C_D0324FAA1894"
    xmi.id="EAID_F14A71F2_032E_4318_93E6_B0AED4645309"

UML:Association.connection>
    <UML:AssociationEnd visibility="public" aggregation="none"
        isOrdered="false" targetScope="instance"
        changeable="none" isNavigable="false"
        type="EAID_0BBEB6E2_5B20_467f_B00F_820896A97113">
        <UML:ModelElement.taggedValue>
            <UML:TaggedValue tag="containment"
            value="Unspecified"/>
            <UML:TaggedValue tag="sourcestyle"
            value="Union=0;Derived=0;AllowDuplicates=0;Owned=0;Navigable=Non-Navigable;"/>
            <UML:TaggedValue tag="ea_end" value="source"/>
        </UML:ModelElement.taggedValue>
    </UML:AssociationEnd>
    <UML:AssociationEnd visibility="public"
        aggregation="composite" isOrdered="false"
        targetScope="instance" changeable="none"
        isNavigable="true"
        type="EAID_78701929_8194_418c_A1AF_12F454CA06E8"

        
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
        
        
"""
def ns(path, nsp=UML):
    """utility function to put namespace in for tags e.g. {http://schemas.openehr.org/v1}tag"""
    
    if path[-1] == '/':
        path = path[:-1]
    if path.startswith('.//'):
        result = path.replace('.//', './/%s' % nsp)
    else:
        result = '%s%s' % (nsp, path.replace('/', '/%s' % nsp))
    return result

def strip_tag(s, sep='::'):
    """stips prefix from tags, eg DCM::"""
    i = s.find(sep)
    if i > -1:
        return s[i+len(sep):]
    else:
        return s

def get_metadata(node):
    """docstring for self._get_metadata"""
    result = {}
    for m in node.findall(ns("TaggedValue")):
        result.setdefault(strip_tag(m.attrib['tag']), []).append(m.attrib.get('value', '-'))
    for k, v in result.items():
        result[k] = ' | '.join(v)
    return result

class Association(object):
    """docstring for Association
    """
    def __init__(self, node):
        super(Association, self).__init__()
        self.node = node
        self.metadata = get_metadata(node.find(ns("ModelElement.taggedValue")))
        self.id = self.metadata['ea_localid']
        self.source = self.metadata['ea_sourceID']
        self.target = self.metadata['ea_targetID']

    def get_cardinality(self):
        return self.metadata.get('lb', '')
    cardinality = property(get_cardinality) 
    
class ModelNode(object):
    """docstring for DCM_Class"""
    def __init__(self, node):
        super(ModelNode, self).__init__()
        self.node = node
        self.name = node.attrib['name']
        try:
            self.stereotype = node.find(ns("ModelElement.stereotype/Stereotype")).attrib['name']
        except AttributeError:
            self.stereotype = 'unknown'
        self.metadata = get_metadata(node.find(ns("ModelElement.taggedValue")))
        self.id = self.metadata['ea_localid']
        self.valueset = list(node.findall(ns("Classifier.feature/Attribute")))
        self.parent = None
        self.children = []
                
    def write_valueset(self, node):
        """docstring for _add_valueset"""
        # <valueset>
        #     <value score="4">Spontaneous</value>
        # </valueset>
        vs = ET.Element("valueset")
        for value in self.valueset:
            v = ET.Element("value")
            v.text = value.attrib['name']
            score = value.find(ns('Attribute.initialValue/Expression[@body]'))
            if not score is None:
                v.attrib['score'] = score.attrib.get('body', '-')
            vs.append(v)
        node.append(vs)
    
    def write_to_output(self, node):
        """docstring for write_to_output"""
        pass
        
class DCM(object):
    """docstring for OptProcessor"""
    def __init__(self):
        super(DCM, self).__init__()
        self.root = ET.Element("clinicaltemplate")
        self.output = ET.ElementTree(self.root)
        self.item_id = 10
        self.model_dict = self.associations = self.assoc_dict = self.rootconcept = None
        
    def _find_rootconcept(self):
        """docstring for _find_rootconcept"""
        for n in self.model_dict.values():
            if n.stereotype == 'rootconcept':
                self.rootconcept = n
                return n.name
        return ''
    
    def name(self):
        """docstring for name"""
        return self.metadata.get('Name', 'error-no-name-set')
                
    def _get_docs(self):
        """docstring for _get_docs"""
        docs = {}
        
        # looking in TaggedValue, but some of text is in Namespace.ownedElement
        # fragmented and inconsistent in xmi
        
        for k, node in self.content.items():
            if k != 'Information Model':
                try:
                    txt = node.find(ns(".//TaggedValue[@tag='documentation']")).attrib['value']
                except AttributeError:
                    txt = '-'
                docs[k] = txt
        return docs
        
    def _get_assocs(self):
        """docstring for _link_assocs"""
        infomodel = self.content['Information Model']
        self.associations = [Association(n)
            for n in infomodel.findall(ns('Namespace.ownedElement/Association'))]
            
    def _get_concepts(self):
        """docstring for _link_assocs"""
        infomodel = self.content['Information Model']
        nodes = [ModelNode(n)
            for n in infomodel.findall(ns('Namespace.ownedElement/Class'))]
        self.model_dict = dict([(n.id, n) for n in nodes])
        
    def _valuetype_for_concept(self, concept):
        """docstring for fname"""
        if concept.valueset:
            return 'ordinal_list'
        if (concept.stereotype == 'state' and 
            (concept.metadata.get('genlinks', 'no genlink') == 'Parent=BL;')):
            return 'yes_no'
        return VALUETYPES.get(concept.stereotype, 'freetext') #'freetext'
        
    def _make_links(self, concept=None, i=0):
        """docstring for _make_links"""
        for a in self.associations:
            parent = self.model_dict[a.target]
            child = self.model_dict[a.source]
            parent.children.append(child)
            child.parent = parent
            child.cardinality = a.cardinality
            
    def _write_metadata_to_output(self):
        root = ET.Element("metadata")
        self.root.append(root)
        self.item_id = 10
        for k, v in self.metadata.items():
            # <item id="m010" label="label">My second DCM</item>
            attrs = { 'id': 'm%04d' % self.item_id, 'label': k }
            n = ET.Element("item", attrs)
            n.text = v
            self.item_id += 10
            root.append(n)

    def _write_docs_to_output(self):
        root = ET.Element("documentation")
        self.root.append(root)
        self.item_id = 10
        for k, v in self.documentation.items():
            attrs = { 'id': 'd%04d' % self.item_id, 'label': k,  'markup': 'textile' }
            n = ET.Element("item", attrs)
            n.text = v
            root.append(n)
        
    def _write_infomodel_to_output(self, node, concept=None):
        """docstring for _write_to_output"""
        def _write_info(self, node, concept=None):
            """docstring for _write_info"""
            if concept is None:
                concept = self.rootconcept
                n = node
            else:
                # id="i001" label="Total Glasgow Coma Scale Score" valueType="integer"
                attrs = { 'id': 'i%04d' % self.item_id, 'label': concept.name,
                    'cardinality': concept.cardinality,
                    'valueType': self._valuetype_for_concept(concept) }
                n = ET.Element("item", attrs)
                self.item_id += 10
                if concept.valueset:
                    concept.write_valueset(n)
                node.append(n)
            for i, c in enumerate(concept.children):
                _write_info(self, n, c)
        self.item_id = 10
        _write_info(self, node)
        
    def process(self, tree, infomodel=True, docs=True, metadata=True):
        xmi = tree.find('XMI.content')
        self.content = dict([(c.attrib['name'], c)
            for c in  xmi.findall(ns("Model/Namespace.ownedElement/Package/Namespace.ownedElement/Package"))])
        self.metadata = get_metadata(xmi)
        self.documentation = self._get_docs()
        self._get_concepts()
        self._find_rootconcept()
        self._get_assocs()
        self._make_links()
        n = ET.Element("model")
        self.root.append(n)
        if metadata:
            self._write_metadata_to_output()
        if docs:
            self._write_docs_to_output()
        if infomodel:
            self._write_infomodel_to_output(n)

    def get_output(self):
        """docstring for dump_output"""
        return ET.tostring(self.root)

