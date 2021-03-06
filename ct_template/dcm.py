from django.template.defaultfilters import slugify
import elementtree.ElementTree as ET
# from xml.etree import ElementTree as ET


UML = "{omg.org/UML1.3}"
## DOC_HEADINGS = ('',)

VALUETYPES = {
    'data': 'integer',
    'container': 'group',
    }

DATATYPES = {
    'CD': None,
    'BL': None,
    'ST': None,
    'PQ': None,
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
        result.setdefault(strip_tag(m.attrib['tag']), []).append(m.attrib.get('value', '-').replace('\n', '||'))
    for k, v in result.items():
        result[k] = ' | '.join(v)
    name = result.get('Name', None)
    if name is None:
        name = result.get('DCM.Name', 'error-no-name-set')
    result['Name'] = name
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
        self.xmi_id = node.attrib.get('xmi.id', '')
        self.description = self.metadata.get('documentation', '')
        self.datatype = None
        self.valueset = list(node.findall(ns("Classifier.feature/Attribute")))
        self.parent = None
        self.children = []
        self.definition_codes = []

    def write_definition_codes(self, node):
        tbs = ET.Element("termbindings")
        for dc in self.definition_codes:
            tb = ET.Element("termbinding", {})
            tb.text = dc
            tbs.append(tb)
        node.append(tbs)
    
    def write_valueset(self, node):
        """docstring for _add_valueset"""
        # <valueset>
        #     <value score="4">Spontaneous</value>
        # </valueset>
        vs = ET.Element("valueset")
        for value in self.valueset:
            metadata = get_metadata(value.find(ns("ModelElement.taggedValue")))
            # print metadata
            # print
            attrs = {'description': metadata.get('description', ''), 'defcode': metadata.get('DefinitionCode', '')}
            v = ET.Element("value", attrs)
            v.text = value.attrib['name']
            score = value.find(ns('Attribute.initialValue/Expression[@body]'))
            if not score is None:
                v.attrib['score'] = score.attrib.get('body', '')
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
        self.infomodel = self.model_dict = self.xmi_id_dict = self.associations = self.assoc_dict = self.rootconcept = None
        
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
                
    def version(self):
        """docstring for version"""
        return self.metadata.get('Version', 'error-no-version-set')

    def _get_docs(self):
        """docstring for _get_docs"""
        docs = {}
        
        # looking in TaggedValue, but some of text is in Namespace.ownedElement
        # fragmented and inconsistent in xmi
        
        for k, node in self.content.items():
            if k.lower() != 'information model':
                try:
                    txt = node.find(ns(".//TaggedValue[@tag='documentation']")).attrib['value']
                except AttributeError:
                    txt = '-'
                docs[k] = txt
        return docs
        
    def _get_assocs(self):
        """docstring for _link_assocs"""
        self.associations = [Association(n)
            for n in self.infomodel.findall(ns('Namespace.ownedElement/Association'))]

    def _get_datatypes(self):
        for gen in self.infomodel.findall(ns('Namespace.ownedElement/Generalization')):
            metadata = get_metadata(gen.find(ns("ModelElement.taggedValue")))
            dt = metadata.get('ea_targetName', '-')
            if dt in DATATYPES:
                node = self.model_dict[metadata.get('ea_sourceID', '-')]
                # print node.name
                node.datatype = dt
                # print metadata.get('ea_sourceName', '-'), metadata.get('ea_sourceID', '-'), dt

    def _get_definitioncodes(self, xmi):
        print 'def codes:'
        ind = [''] + ['%s' % d for d in range(1,10)]
        for i in ind:
            for c in xmi.findall(ns("TaggedValue[@tag='DCM::DefinitionCode%s']"%i)):
                value = c.attrib.get('value', None)
                node_id = c.attrib.get('modelElement', None)
                if value and node_id:
                    node = self.xmi_id_dict[node_id]
                    node.definition_codes.append(value)
                    print 'code: ', value, '->', node.name

    def _get_concepts(self):
        """docstring for _link_assocs"""
        nodes = [ModelNode(n)
            for n in self.infomodel.findall(ns('Namespace.ownedElement/Class'))]
        self.model_dict = dict([(n.id, n) for n in nodes])
        self.xmi_id_dict = dict([(n.xmi_id, n) for n in nodes if n.xmi_id])
        
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
            if self.topdown:
                parent = self.model_dict[a.target]
                child = self.model_dict[a.source]
            else:
                parent = self.model_dict[a.source]
                child = self.model_dict[a.target]
            parent.children.append(child)
            child.parent = parent
            child.cardinality = a.cardinality
            # print parent.id, parent.name, child.id, child.name
            
    def _write_metadata_to_output(self):
        root = ET.Element("metadata")
        self.root.append(root)
        self.item_id = 10

        attrs = { 'id': 'm%04d' % self.item_id, 'label': 'Name' }
        n = ET.Element("item", attrs)
        n.text = self.rootconcept.name
        self.item_id += 10
        root.append(n)
        attrs = { 'id': 'm%04d' % self.item_id, 'label': 'Description' }
        n = ET.Element("item", attrs)
        n.text = self.rootconcept.description
        self.item_id += 10
        root.append(n)
        attrs = { 'id': 'm%04d' % self.item_id, 'label': 'Coding' }
        n = ET.Element("item", attrs)
        n.text = ', '.join(self.rootconcept.definition_codes)
        self.item_id += 10
        root.append(n)

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
            self.item_id += 10
            root.append(n)
            
    def _write_infomodel_to_output(self, node, concept=None, test=False):
        """docstring for _write_to_output"""
        def _write_info(self, node, concept=None, test=test, level=0):
            """docstring for _write_info"""
            if concept is None:
                concept = self.rootconcept
                n = node
            else:
                # id="i001" label="Total Glasgow Coma Scale Score" valueType="integer"
                attrs = { 'id': 'i%04d' % self.item_id, 'label': concept.name,
                    'description': concept.description,
                    'cardinality': concept.cardinality,
                    'datatype': concept.datatype or '',
                    'valueType': self._valuetype_for_concept(concept) }
                n = ET.Element("item", attrs)
                self.item_id += 10
                if concept.valueset:
                    concept.write_valueset(n)
                if concept.definition_codes:
                    concept.write_definition_codes(n)
                node.append(n)
                if test:
                    print '-'*level, concept.name
            for i, c in enumerate(concept.children):
                _write_info(self, n, c, test, level+1)
        if test:
            print 'root', self.rootconcept.id, self.rootconcept.name, self.rootconcept.definition_codes
            for c in self.model_dict.values():
                print c.id, c.xmi_id, c.name, c.parent.name if c.parent else '---'

        self.item_id = 10
        _write_info(self, node)
        
    def process(self, tree, infomodel=True, docs=True, metadata=True, topdown=True, test=False):
        self.topdown = topdown
        xmi = tree.find('XMI.content')
        self.content = dict([(c.attrib['name'], c)
            for c in  xmi.findall(ns("Model/Namespace.ownedElement/Package/Namespace.ownedElement/Package"))])
        self.infomodel = self.content.get('Information Model', None)
        if self.infomodel is None:
            self.infomodel = self.content['Information model']
        self.metadata = get_metadata(xmi)
        self.documentation = self._get_docs()
        self._get_concepts()
        self._find_rootconcept()
        self._get_assocs()
        self._make_links()
        self._get_datatypes()
        self._get_definitioncodes(xmi)
        n = ET.Element("model")
        self.root.append(n)
        if metadata:
            self._write_metadata_to_output()
        if docs:
            self._write_docs_to_output()
        if infomodel:
            self._write_infomodel_to_output(n, test=test)

    def get_output(self):
        """docstring for dump_output"""
        return ET.tostring(self.root)

