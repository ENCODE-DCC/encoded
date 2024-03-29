from rdflib import ConjunctiveGraph, exceptions, Namespace
from rdflib import RDFS, RDF, BNode
from rdflib.collection import Collection
from .ntr_terms import (
    ntr_assays,
    ntr_biosamples
)
from .manual_slims import slim_shims
import json

EPILOG = __doc__

OWLNS = Namespace("http://www.w3.org/2002/07/owl#")
OBO_OWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")
EFO = Namespace("http://www.ebi.ac.uk/efo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")

OBO_Synonym = OBO["IAO_0000118"]
Synonym = OBO_OWL["hasExactSynonym"]
Ontology = OWLNS["Ontology"]

Restriction = OWLNS["Restriction"]
Class = OWLNS["Class"]
Thing = OWLNS["Thing"]
OnProperty = OWLNS["onProperty"]
SomeValuesFrom = OWLNS["someValuesFrom"]
IntersectionOf = OWLNS["intersectionOf"]

PART_OF = "http://purl.obolibrary.org/obo/BFO_0000050"
DEVELOPS_FROM = "http://purl.obolibrary.org/obo/RO_0002202"
HUMAN_TAXON = "http://purl.obolibrary.org/obo/NCBITaxon_9606"
HAS_PART = "http://purl.obolibrary.org/obo/BFO_0000051"
DERIVES_FROM = "http://purl.obolibrary.org/obo/RO_0001000"
ACHIEVES_PLANNED_OBJECTIVE = "http://purl.obolibrary.org/obo/OBI_0000417"
DEFAULT_LANGUAGE = "en"

developental_slims = {
    'UBERON:0000926': 'mesoderm',
    'UBERON:0000924': 'ectoderm',
    'UBERON:0000925': 'endoderm'
}

system_slims = {
    'UBERON:0001015': 'musculature',
    'UBERON:0000949': 'endocrine system',
    'UBERON:0002330': 'exocrine system',
    'UBERON:0000990': 'reproductive system',
    'UBERON:0001004': 'respiratory system',
    'UBERON:0001007': 'digestive system',
    'UBERON:0001008': 'excretory system',
    'UBERON:0001009': 'circulatory system',
    'UBERON:0001434': 'skeletal system',
    'UBERON:0002405': 'immune system',
    'UBERON:0002416': 'integumental system',
    'UBERON:0001032': 'sensory system',
    'UBERON:0001017': 'central nervous system',
    'UBERON:0000010': 'peripheral nervous system'
}

organ_slims = {
    'UBERON:0002369': 'adrenal gland',
    'UBERON:0002110': 'gallbladder',
    'UBERON:0002106': 'spleen',
    'UBERON:0001043': 'esophagus',
    'UBERON:0000004': 'nose',
    'UBERON:0000056': 'ureter',
    'UBERON:0000057': 'urethra',
    'UBERON:0000059': 'large intestine',
    'UBERON:0000165': 'mouth',
    'UBERON:0000945': 'stomach',
    'UBERON:0000948': 'heart',
    'UBERON:0000955': 'brain',
    'UBERON:0000970': 'eye',
    'UBERON:0000991': 'gonad',
    'UBERON:0001255': 'urinary bladder',
    'UBERON:0001264': 'pancreas',
    'UBERON:0001474': 'bone element',
    'UBERON:0002048': 'lung',
    'UBERON:0002097': 'skin of body',
    'UBERON:0002107': 'liver',
    'UBERON:0002108': 'small intestine',
    'UBERON:0002113': 'kidney',
    'UBERON:0002240': 'spinal cord',
    'UBERON:0002367': 'prostate gland',
    'UBERON:0002370': 'thymus',
    'UBERON:0003126': 'trachea',
    'UBERON:0001723': 'tongue',
    'UBERON:0001737': 'larynx',
    'UBERON:0006562': 'pharynx',
    'UBERON:0001103': 'diaphragm',
    'UBERON:0002185': 'bronchus',
    'UBERON:0000029': 'lymph node',
    'UBERON:0001132': 'parathyroid gland',
    'UBERON:0002046': 'thyroid gland',
    'UBERON:0001981': 'blood vessel',
    'UBERON:0001473': 'lymphatic vessel',
    'UBERON:0000178': 'blood',
    'UBERON:0007844': 'cartilage element',
    'UBERON:0001690': 'ear',
    'UBERON:0001987': 'placenta',
    'UBERON:0001911': 'mammary gland',
    'UBERON:0000007': 'pituitary gland',
    'UBERON:0016887': 'extraembryonic component',
    'UBERON:0001013': 'adipose tissue',
    'UBERON:0000310': 'breast',
    'UBERON:0000989': 'penis',
    'UBERON:0004288': 'skeleton',
    'UBERON:0000995': 'uterus',
    'UBERON:0000996': 'vagina',
    'UBERON:0000992': 'ovary',
    'UBERON:0000473': 'testis',
    'UBERON:0003509': 'arterial blood vessel',
    'UBERON:0001638': 'vein',
    'UBERON:0000160': 'intestine',
    'UBERON:0002384': 'connective tissue',
    'UBERON:0002101': 'limb',
    'UBERON:0000922': 'embryo',
    'UBERON:0000383': 'musculature of body',
    'UBERON:0001021': 'nerve',
    'UBERON:0002371': 'bone marrow',
    'UBERON:0006314': 'bodily fluid',
    'UBERON:0002049': 'vasculature',
    'UBERON:0000483': 'epithelium',
    'UBERON:0002407': 'pericardium',
    'UBERON:0001744': 'lymphoid tissue',
    'UBERON:0001155': 'colon',
    'UBERON:0003547': 'brain meninx',
    'UBERON:0001350': 'coccyx',
    'UBERON:0002368': 'endocrine gland',
    'UBERON:0002365': 'exocrine gland',
    'UBERON:0002073': 'hair follicle',
    'UBERON:0005057': 'immune organ',
    'UBERON:0001817': 'lacrimal gland',
    'UBERON:0002182': 'main bronchus',
    'UBERON:0001829': 'major salivary gland',
    'UBERON:0000414': 'mucous gland',
    'UBERON:0001821': 'sebaceous gland',
    'UBERON:0000998': 'seminal vesicle',
    'UBERON:0001820': 'sweat gland',
    'UBERON:0001471': 'skin of prepuce of penis'
}

cell_slims = {
    'CL:0000236': 'B cell',
    'EFO:0001640': 'B cell',# B cell derived cell line
    'EFO:0001639': 'cancer cell', # cancer cell line
    'CL:0002494': 'cardiocyte',
    'CL:0002320': 'connective tissue cell',
    'CL:0002321': 'embryonic cell',
    'CL:0000115': 'endothelial cell',
    'EFO:0005730': 'endothelial cell', # endothelial cell derived cell line
    'CL:0000066': 'epithelial cell',
    'EFO:0001641': 'epithelial cell', # epithelial cell derived cell line
    'CL:0000057': 'fibroblast',
    'EFO:0002009': 'fibroblast',# fibroblast derived cell line
    'CL:0000988': 'hematopoietic cell',
    'EFO:0004905': 'induced pluripotent stem cell',
    'EFO:0005740': 'induced pluripotent stem cell', # induced pluripotent stem cell derived cell line
    'CL:0000312': 'keratinocyte',
    'CL:0000738': 'leukocyte',
    'EFO:0005292': 'lymphoblast', # lymphoblastoid cell line
    'CL:0000148': 'melanocyte',
    'CL:0000576': 'monocyte',
    'CL:0000763': 'myeloid cell',
    'CL:0000056': 'myoblast',
    'CL:0002319': 'neural cell',
    'EFO:0005214': 'neuroblastoma cell', # neuroblastoma cell line
    'CL:0000669': 'pericyte',
    'CL:0000192': 'smooth muscle cell',
    'EFO:0005735': 'smooth muscle cell', # smooth muscle cell derived cell line
    'CL:0000034': 'stem cell',
    'EFO:0002886': 'stem cell', # stem cell derived cell line
    'CL:0000084': 'T cell',
    'NTR:0000550': 'progenitor cell'
}

assay_slims = {
    # Note shortened synonyms are provided
    'OBI:0000634': 'DNA methylation',  # 'DNA methylation profiling'
    'OBI:0000424': 'Transcription',  # 'transcription profiling'
    'OBI:0001398': 'DNA binding',  # "protein and DNA interaction"
    'OBI:0001854': 'RNA binding',  # "protein and RNA interaction"
    'OBI:0001917': '3D chromatin structure',  # 'chromosome conformation identification objective'
    'OBI:0000870': 'DNA accessibility',  # 'single-nucleotide-resolution nucleic acid structure mapping assay'
    'OBI:0001916': 'Replication timing',
    'OBI:0000435': 'Genotyping',
    'OBI:0000615': 'Proteomics',
    'OBI:0000626': 'DNA sequencing',
    'OBI:0000845': 'RNA structure',
    'OBI:0002082': 'Reporter assay', # 'Reporter gene assay'
    'OBI:0002675': 'Massively parallel reporter assay', 
    'NTR:0000520': 'CRISPR screen',
    'OBI:0000711': 'Library preparation',
    'NTR:0000675': 'Ribosome activity'
}

preferred_name = {
    "OBI:0002117": "WGS",
    "OBI:0001247": "genotyping HTS",
    "OBI:0001332": "DNAme array",
    "OBI:0001335": "microRNA counts",
    "OBI:0001463": "RNA microarray",
    "OBI:0001863": "WGBS",
    "OBI:0001923": "MS-MS",
    "OBI:0001271": "RNA-seq",
    "OBI:0000716": "ChIP-seq",
    "OBI:0001853": "DNase-seq",
    "OBI:0001920": "Repli-seq",
    "OBI:0001864": "RAMPAGE",
    "OBI:0001393": "genotyping array",
    "OBI:0002042": "Hi-C",
    "OBI:0002457": "PRO-seq",
    "OBI:0002458": "4C",
    "OBI:0002629": "direct RNA-seq",
    "OBI:0002144": "Circulome-seq",
    "OBI:0002459": "genotyping HiC",
    "OBI:0002675": "MPRA",
    "OBI:0002571": "polyA plus RNA-seq",
    "OBI:0002572": "polyA minus RNA-seq",
    "OBI:0002631": "scRNA-seq",
    "OBI:0002112": "small RNA-seq",
    "OBI:0002083": "enhancer reporter assay",
    "OBI:0002762": "snATAC-seq",
    "OBI:0002764": "scATAC-seq",
    "OBI:0002038": "Ribo-seq",
    "OBI:0002984": "capture Hi-C",
    "OBI:0003033": "CUT&RUN",
    "OBI:0003034": "CUT&Tag",
    "OBI:0003106": "seqFISH"
}

category_slims = {
    'OBI:0000634': 'DNA methylation profiling',
    'OBI:0000424': 'transcription profiling',
    'OBI:0000435': 'genotyping',
    'OBI:0000615': 'proteomics',
    'OBI:0001916': 'replication',
    'OBI:0001398': "protein and DNA interaction",
    'OBI:0001854': "protein and RNA interaction"
}

objective_slims = {
    'OBI:0000218': 'cellular feature identification objective',
    'OBI:0001691': 'cellular structure feature identification objective',
    'OBI:0001916': 'DNA replication identification objective',
    'OBI:0001917': 'chromosome conformation identification objective',
    'OBI:0001234': 'epigenetic modification identification objective',
    'OBI:0001331': 'transcription profiling identification objective',
    'OBI:0001690': 'molecular function identification objective',
    'OBI:0000268': 'organism feature identification objective',
    'OBI:0001623': 'organism identification objective',
    'OBI:0001398': 'protein and DNA interaction identification objective',
    'OBI:0001854': 'protein and RNA interaction identification objective'
}

type_slims = {
    'OBI:0001700': 'immunoprecipitation assay',
    'OBI:0000424': 'transcription profiling assay',
    'OBI:0000634': 'DNA methylation profiling assay',
    'OBI:0000435': 'genotyping assay'
}


class Inspector(object):

    """ Class that includes methods for querying an RDFS/OWL ontology """

    def __init__(self, uri, language=""):
        super(Inspector, self).__init__()
        self.rdfGraph = ConjunctiveGraph()
        try:
            self.rdfGraph.parse(uri, format="application/rdf+xml")
        except:
            try:
                self.rdfGraph.parse(uri, format="n3")
            except:
                raise exceptions.Error("Could not parse the file! Is `%s` a valid RDF/OWL ontology?" % uri)
        finally:
            self.baseURI = self.get_OntologyURI() or uri
            self.allclasses = self.__getAllClasses(includeDomainRange=True, includeImplicit=True, removeBlankNodes=False, excludeRDF_OWL=False)

    def get_OntologyURI(self, return_as_string=True):
        test = [x for x, y, z in self.rdfGraph.triples((None, RDF.type, Ontology))]
        if test:
            if return_as_string:
                return str(test[0])
            else:
                return test[0]
        else:
            return None

    def __getAllClasses(self, classPredicate="", includeDomainRange=False, includeImplicit=False, removeBlankNodes=True, addOWLThing=True, excludeRDF_OWL=True):

        rdfGraph = self.rdfGraph
        exit = {}

        def addIfYouCan(x, mydict):
            if excludeRDF_OWL:
                if x.startswith('http://www.w3.org/2002/07/owl#') or  \
                   x.startswith("http://www.w3.org/1999/02/22-rdf-syntax-ns#") or \
                   x.startswith("http://www.w3.org/2000/01/rdf-schema#"):
                    return mydict
            if x not in mydict:
                mydict[x] = None
            return mydict

        if addOWLThing:
            exit = addIfYouCan(Thing, exit)

        if classPredicate == "rdfs" or classPredicate == "":
            for s in rdfGraph.subjects(RDF.type, RDFS.Class):
                exit = addIfYouCan(s, exit)

        if classPredicate == "owl" or classPredicate == "":
            for s in rdfGraph.subjects(RDF.type, Class):
                exit = addIfYouCan(s, exit)

        if includeDomainRange:
            for o in rdfGraph.objects(None, RDFS.domain):
                exit = addIfYouCan(o, exit)
            for o in rdfGraph.objects(None, RDFS.range):
                exit = addIfYouCan(o, exit)

        if includeImplicit:
            for s, v, o in rdfGraph.triples((None, RDFS.subClassOf, None)):
                exit = addIfYouCan(s, exit)
                exit = addIfYouCan(o, exit)
            for o in rdfGraph.objects(None, RDF.type):
                exit = addIfYouCan(o, exit)

        # get a list
        exit = exit.keys()
        if removeBlankNodes:
            exit = [x for x in exit if not isBlankNode(x)]
        return sort_uri_list_by_name(exit)

    def __getTopclasses(self, classPredicate=''):
        returnlist = []

        for eachclass in self.__getAllClasses(classPredicate):
            x = self.get_classDirectSupers(eachclass)
            if not x:
                returnlist.append(eachclass)
        return sort_uri_list_by_name(returnlist)

    def __getTree(self, father=None, out=None):
        if not father:
            out = {}
            topclasses = self.toplayer
            out[0] = topclasses

            for top in topclasses:
                children = self.get_classDirectSubs(top)
                out[top] = children
                for potentialfather in children:
                    self.__getTree(potentialfather, out)

            return out

        else:
            children = self.get_classDirectSubs(father)
            out[father] = children
            for ch in children:
                self.__getTree(ch, out)

    def __buildClassTree(self, father=None, out=None):
        if not father:
            out = {}
            topclasses = self.toplayer
            out[0] = [Thing]
            out[Thing] = sort_uri_list_by_name(topclasses)
            for top in topclasses:
                children = self.get_classDirectSubs(top)
                out[top] = sort_uri_list_by_name(children)
                for potentialfather in children:
                    self.__buildClassTree(potentialfather, out)
            return out
        else:
            children = self.get_classDirectSubs(father)
            out[father] = sort_uri_list_by_name(children)
            for ch in children:
                self.__buildClassTree(ch, out)

    # methods for getting ancestores and descendants of classes: by default, we do not include blank nodes
    def get_classDirectSupers(self, aClass, excludeBnodes=True, sortUriName=False):
        returnlist = []
        for o in self.rdfGraph.objects(aClass, RDFS.subClassOf):
            if not (o == Thing):
                if excludeBnodes:
                    if not isBlankNode(o):
                        returnlist.append(o)
                else:
                    returnlist.append(o)
        if sortUriName:
            return sort_uri_list_by_name(remove_duplicates(returnlist))
        else:
            return remove_duplicates(returnlist)

    def get_classDirectSubs(self, aClass, excludeBnodes=True):
        returnlist = []
        for s, v, o in self.rdfGraph.triples((None, RDFS.subClassOf, aClass)):
            if excludeBnodes:
                if not isBlankNode(s):
                    returnlist.append(s)
            else:
                returnlist.append(s)
        return sort_uri_list_by_name(remove_duplicates(returnlist))

    def get_classSiblings(self, aClass, excludeBnodes=True):
        returnlist = []
        for father in self.get_classDirectSupers(aClass, excludeBnodes):
            for child in self.get_classDirectSubs(father, excludeBnodes):
                if child != aClass:
                    returnlist.append(child)

        return sort_uri_list_by_name(remove_duplicates(returnlist))

    def entitySynonyms(self, anEntity, language=DEFAULT_LANGUAGE, getall=True):
        if getall:
            temp = []
            # Uberon synonyms
            for o in self.rdfGraph.objects(anEntity, Synonym):
                temp += [o]
            # EFO synonyms
            for o in self.rdfGraph.objects(anEntity, Synonym):
                temp += [o]
            # OBI synonyms
            for o in self.rdfGraph.objects(anEntity, OBO_Synonym):
                temp += [o]
            return temp
        else:
            for o in self.rdfGraph.objects(anEntity, Synonym):
                if getattr(o, 'language') and getattr(o, 'language') == language:
                    return o
            return ""

    def classFind(self, name, exact=False):
        temp = []
        if name:
            for x in self.allclasses:
                if exact:
                    if x.__str__().lower() == str(name).lower():
                        return [x]
                else:
                    if x.__str__().lower().find(str(name).lower()) >= 0:
                        temp.append(x)
        return temp


def inferNamespacePrefix(aUri):
    stringa = aUri.__str__()
    try:
        prefix = stringa.replace("#", "").split("/")[-1]
    except:
        prefix = ""
    return prefix


def sort_uri_list_by_name(uri_list):

    def get_last_bit(uri_string):
        try:
            x = uri_string.split("#")[1]
        except:
            x = uri_string.split("/")[-1]
        return x

    try:
        return sorted(uri_list, key=lambda x: get_last_bit(x.__str__()))
    except:
        # TODO: do more testing.. maybe use a unicode-safe method instead of __str__
        print("Error in <sort_uri_list_by_name>: possibly a UnicodeEncodeError")
        return uri_list


def remove_duplicates(seq, idfun=None):
    if seq:
        if idfun is None:
            def idfun(x):
                return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            if marker in seen:
                continue
            seen[marker] = 1
            result.append(item)
        return result
    else:
        return []


def isBlankNode(aClass):
    ''' Checks for blank node '''
    if type(aClass) == BNode:
        return True
    else:
        return False


def splitNameFromNamespace(aUri):
    stringa = aUri.__str__()
    try:
        ns = stringa.split("#")[0]
        name = stringa.split("#")[1]
    except:
        ns = stringa.rsplit("/", 1)[0]
        name = stringa.rsplit("/", 1)[1]
    return (name, ns)


def iterativeChildren(nodes, terms, closure):
    if closure == 'data':
        data = 'data'
    else:
        data = 'data_with_develops_from'
    results = []
    while 1:
        newNodes = []
        if len(nodes) == 0:
            break
        for node in nodes:
            results.append(node)
            if terms[node][data]:
                for child in terms[node][data]:
                    if child not in results:
                        newNodes.append(child)
        nodes = list(set(newNodes))
    return list(set(results))


def getSlims(goid, terms, slimType):
    ''' Get Slims '''

    slims = []
    slimTerms = {}
    if slimType == 'developmental':
        slimTerms = developental_slims
    elif slimType == 'organ':
        slimTerms = organ_slims
    elif slimType == 'cell':
        slimTerms = cell_slims
    elif slimType == 'system':
        slimTerms = system_slims
    elif slimType == 'assay':
        slimTerms = assay_slims
    elif slimType == 'category':
        slimTerms = category_slims
    elif slimType == 'objective':
        slimTerms = objective_slims
    elif slimType == 'type':
        slimTerms = type_slims
    for slimTerm in slimTerms:
        if slimType == 'developmental':
            if slimTerm in terms[goid]['closure_with_develops_from']:
                slims.append(slimTerms[slimTerm])
        else:
            if slimTerm in terms[goid]['closure']:
                slims.append(slimTerms[slimTerm])

    if slim_shims.get(slimType, {}):
        # Overrides all Ontology based-slims
        shim = slim_shims[slimType].get(goid, '')
        if shim:
            slims = []
            for i in shim:
                slims.append(i)
    return slims


def getTermStructure():
    return {
        'id': '',
        'name': '',
        'preferred_name': '',
        'parents': [],
        'part_of': [],
        'has_part': [],
        'derives_from': [],
        'develops_from': [],
        'achieves_planned_objective': [],
        'organs': [],
        'cells': [],
        'closure': [],
        'slims': [],
        'data': [],
        'closure_with_develops_from': [],
        'data_with_develops_from': [],
        'synonyms': [],
        'category': [],
        'assay': [],
        'types': [],
        'objectives': []
    }


def main():
    ''' Downloads UBERON, EFO, OBI and CLO ontologies and create a JSON file '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Get Uberon, EFO, OBI, and CLO ontologies and generate the JSON file", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--uberon-url', help="Uberon version URL")
    parser.add_argument('--cl-url', help="CL version URL")
    parser.add_argument('--efo-url', help="EFO version URL")
    parser.add_argument('--obi-url', help="OBI version URL")
    parser.add_argument('--clo-url', help="CLO version URL")
    parser.add_argument('--doid-url', help="DOID version URL")
    args = parser.parse_args()

    uberon_url = args.uberon_url
    cl_url = args.cl_url
    efo_url = args.efo_url
    obi_url = args.obi_url
    clo_url = args.clo_url
    doid_url = args.doid_url
    whitelist = [uberon_url, efo_url, obi_url, doid_url, cl_url]

    terms = {}
    # Run on ontologies defined in whitelist
    for url in whitelist:
        data = Inspector(url)
        for c in data.allclasses:
            if isBlankNode(c):
                for o in data.rdfGraph.objects(c, RDFS.subClassOf):
                    if isBlankNode(o):
                        pass
                    else:
                        for o1 in data.rdfGraph.objects(c, IntersectionOf):
                            collection = Collection(data.rdfGraph, o1)
                            col_list = []
                            for col in data.rdfGraph.objects(collection[1]):
                                col_list.append(col.__str__())
                            if HUMAN_TAXON in col_list:
                                if PART_OF in col_list:
                                    for subC in data.rdfGraph.objects(c, RDFS.subClassOf):
                                        term_id = splitNameFromNamespace(collection[0])[0].replace('_', ':')
                                        if term_id not in terms:
                                            terms[term_id] = getTermStructure()
                                        terms[term_id]['part_of'].append(splitNameFromNamespace(subC)[0].replace('_', ':'))
                                elif DEVELOPS_FROM in col_list:
                                    for subC in data.rdfGraph.objects(c, RDFS.subClassOf):
                                        term_id = splitNameFromNamespace(collection[0])[0].replace('_', ':')
                                        if term_id not in terms:
                                            terms[term_id] = getTermStructure()
                                        terms[term_id]['develops_from'].append(splitNameFromNamespace(subC)[0].replace('_', ':'))
            else:
                term_id = splitNameFromNamespace(c)[0].replace('_', ':')
                if term_id not in terms:
                    terms[term_id] = getTermStructure()
                terms[term_id]['id'] = term_id
                
                try:
                    terms[term_id]['name'] = data.rdfGraph.label(c).__str__()
                except:
                    terms[term_id]['name'] = ''

                terms[term_id]['preferred_name'] = preferred_name.get(term_id, '')
                # Get all parents
                for parent in data.get_classDirectSupers(c, excludeBnodes=False):
                    if isBlankNode(parent):
                        for s, v, o in data.rdfGraph.triples((parent, OnProperty, None)):
                            if o.__str__() == PART_OF:
                                for o1 in data.rdfGraph.objects(parent, SomeValuesFrom):
                                    if not isBlankNode(o1):
                                        terms[term_id]['part_of'].append(splitNameFromNamespace(o1)[0].replace('_', ':'))
                            elif o.__str__() == DEVELOPS_FROM:
                                for o1 in data.rdfGraph.objects(parent, SomeValuesFrom):
                                    if not isBlankNode(o1):
                                        terms[term_id]['develops_from'].append(splitNameFromNamespace(o1)[0].replace('_', ':'))
                            elif o.__str__() == HAS_PART:
                                for o1 in data.rdfGraph.objects(parent, SomeValuesFrom):
                                    if not isBlankNode(o1):
                                        terms[term_id]['has_part'].append(splitNameFromNamespace(o1)[0].replace('_', ':'))
                            elif o.__str__() == DERIVES_FROM:
                                for o1 in data.rdfGraph.objects(parent, SomeValuesFrom):
                                    if not isBlankNode(o1):
                                        terms[term_id]['derives_from'].append(splitNameFromNamespace(o1)[0].replace('_', ':'))
                                    else:
                                        for o2 in data.rdfGraph.objects(o1, IntersectionOf):
                                            for o3 in data.rdfGraph.objects(o2, RDF.first):
                                                if not isBlankNode(o3):
                                                    terms[term_id]['derives_from'].append(splitNameFromNamespace(o3)[0].replace('_', ':'))
                                            for o3 in data.rdfGraph.objects(o2, RDF.rest):
                                                for o4 in data.rdfGraph.objects(o3, RDF.first):
                                                    for o5 in data.rdfGraph.objects(o4, SomeValuesFrom):
                                                        for o6 in data.rdfGraph.objects(o5, IntersectionOf):
                                                            for o7 in data.rdfGraph.objects(o6, RDF.first):
                                                                if not isBlankNode(o7):
                                                                    terms[term_id]['derives_from'].append(splitNameFromNamespace(o7)[0].replace('_', ':'))
                                                                    for o8 in data.rdfGraph.objects(o6, RDF.rest):
                                                                        for o9 in data.rdfGraph.objects(o8, RDF.first):
                                                                            if not isBlankNode(o9):
                                                                                terms[term_id]['derives_from'].append(splitNameFromNamespace(o9)[0].replace('_', ':'))
                            elif o.__str__() == ACHIEVES_PLANNED_OBJECTIVE:
                                for o1 in data.rdfGraph.objects(parent, SomeValuesFrom):
                                    if not isBlankNode(o1):
                                        terms[term_id]['achieves_planned_objective'].append(splitNameFromNamespace(o1)[0].replace('_', ':'))
                    else:
                        terms[term_id]['parents'].append(splitNameFromNamespace(parent)[0].replace('_', ':'))
                
                for syn in data.entitySynonyms(c):
                    try:
                        terms[term_id]['synonyms'].append(syn.__str__())
                    except:
                        pass

    # Get only CLO terms from the CLO owl file
    data = Inspector(clo_url)
    for c in data.allclasses:
        if c.startswith('http://purl.obolibrary.org/obo/CLO'):
            term_id = splitNameFromNamespace(c)[0].replace('_', ':')
            if term_id not in terms:
                terms[term_id] = getTermStructure()
                terms[term_id]['name'] = data.rdfGraph.label(c).__str__()
            for syn in data.entitySynonyms(c):
                try:
                    terms[term_id]['synonyms'].append(syn.__str__())
                except:
                    pass

    for term in terms:
        terms[term]['data'] = list(set(terms[term]['parents']) | set(terms[term]['part_of']) | set(terms[term]['derives_from']) | set(terms[term]['achieves_planned_objective']))
        terms[term]['data_with_develops_from'] = list(set(terms[term]['data']) | set(terms[term]['develops_from']))

    for term in terms:
        words = iterativeChildren(terms[term]['data'], terms, 'data')
        for word in words:
            terms[term]['closure'].append(word)

        d = iterativeChildren(terms[term]['data_with_develops_from'], terms, 'data_with_develops_from')
        for dd in d:
            terms[term]['closure_with_develops_from'].append(dd)
       
        terms[term]['closure'].append(term)
        terms[term]['closure_with_develops_from'].append(term)

        terms[term]['systems'] = getSlims(term, terms, 'system')
        terms[term]['organs'] = getSlims(term, terms, 'organ')
        terms[term]['cells'] = getSlims(term, terms, 'cell')
        terms[term]['developmental'] = getSlims(term, terms, 'developmental')
        terms[term]['assay'] = getSlims(term, terms, 'assay')
        terms[term]['category'] = getSlims(term, terms, 'category')
        terms[term]['objectives'] = getSlims(term, terms, 'objective')
        terms[term]['types'] = getSlims(term, terms, 'type')

        del terms[term]['closure'], terms[term]['closure_with_develops_from']
    
    for term in terms:
        del terms[term]['parents'], terms[term]['develops_from']
        del terms[term]['has_part'], terms[term]['achieves_planned_objective']
        del terms[term]['id'], terms[term]['data'], terms[term]['data_with_develops_from']
    
    terms.update(ntr_assays)
    terms.update(ntr_biosamples)
    with open('ontology.json', 'w') as outfile:
        json.dump(terms, outfile)


if __name__ == '__main__':
    main()
