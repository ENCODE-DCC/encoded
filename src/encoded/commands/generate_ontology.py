from rdflib import ConjunctiveGraph, exceptions, Namespace
from rdflib import RDFS, RDF, BNode
from rdflib.collection import Collection
import json

EPILOG = __doc__

OWLNS = Namespace("http://www.w3.org/2002/07/owl#")
OBO_OWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")
EFO = Namespace("http://www.ebi.ac.uk/efo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")

EFO_Synonym = EFO["alternative_term"]
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
ACHIEVES_PLANNED_OBJECTIVE = "http://purl.obolibrary.org/obo/OBI_0000417"
DEFAULT_LANGUAGE = "en"

developental_slims = {
    'UBERON:0000926': 'mesoderm',
    'UBERON:0000924': 'ectoderm',
    'UBERON:0000925': 'endoderm'
}

system_slims = {
    'UBERON:0000383': 'musculature of body',
    'UBERON:0000949': 'endocrine system',
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
    'UBERON:0001630': 'muscle organ',
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
    'UBERON:0001637': 'artery',
    'UBERON:0001638': 'vein',
    'UBERON:0002050': 'embryonic structure',
    'UBERON:0000160': 'intestine',
    'UBERON:0002384': 'connective tissue',
    'UBERON:0002101': 'limb',
    'UBERON:0000922': 'embryo',
    'UBERON:0000383': 'musculature of body',
    'UBERON:0001021': 'nerve',
    'UBERON:0002371': 'bone marrow',
    'UBERON:0006314': 'bodily fluid'
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
    'OBI:0000626': 'DNA sequencing'
}

slim_shims = {
    # this allows us to manually assign term X to slim Y while waiting for ontology updates
    'assay': {
        # DNA accessibility
        'OBI:0001924': 'DNA accessibility',  # 'OBI:0000870' / MNase-seq
        'OBI:0002039': 'DNA accessibility',  # 'OBI:0000870', / ATAC-seq
        'OBI:0001853': 'DNA accessibility',  # 'OBI:0000870', / DNase-seq
        'OBI:0001859': 'DNA accessibility',  # 'OBI:0000870', / OBI:0000424  / FAIRE-seq
        'OBI:0002042': '3D chromatin structure',  # 'OBI:0000870' (Hi-C)
        'OBI:0001848': '3D chromatin structure',  # ChIA-PET / OBI:000870
        'OBI:0001923': 'Proteomics',  # OBI:0000615': 'MS-MS'
        'OBI:0001849': 'Genotyping',  # OBI:0000435 (DNA-PET)
        'OBI:0002044': 'RNA binding',  # OBI:0001854 (RNA-Bind-N-Seq)
        'OBI:0002091': 'Transcription',
        'OBI:0002092': 'Transcription',
        'OBI:0002093': 'Transcription'
    },
    'organ': {
        'EFO:0002782': 'brain',
        'EFO:0002246': 'blood',
        'EFO:0002034': 'blood',
        'EFO:0002055': 'blood',
        'EFO:0002234': 'bone element',
        'EFO:0002330': 'bone element',
        'EFO:0005694': 'bone element',
        'EFO:0003971': 'spleen',
        'EFO:0002357': 'bodily fluid',
        'EFO:0002167': 'bodily fluid',
        'EFO:0002791': 'uterus',
        'EFO:0002184': 'embryo',
        'EFO:0003042': 'embryo',
        'EFO:0003045': 'embryo',
        'EFO:0005483': 'embryo',
        'EFO:0002106': 'musculature of body',
        'EFO:0005722': 'musculature of body',
        'EFO:0005714': 'musculature of body',
        'EFO:0005719': 'blood',
        'EFO:0006711': 'blood',
        'EFO:0007090': 'blood vessel',
        'EFO:0001221': 'bone element',
        'EFO:0005907': 'bone element',
        'EFO:0006710': 'bone element',
        'EFO:0007599': 'bone element',
        'EFO:0007600': 'bone element',
        'EFO:0005234': 'brain',
        'EFO:0002101': 'brain',
        'EFO:0002939': 'brain',
        'EFO:0003072': 'brain',
        'EFO:0005237': 'brain',
        'EFO:0005697': 'brain',
        'EFO:0005721': 'brain',
        'EFO:0005725': 'brain',
        'EFO:0005698': 'brain',
        'EFO:0007075': 'embryo',
        'EFO:0007076': 'embryo',
        'EFO:0007083': 'embryo',
        'EFO:0007086': 'embryo',
        'EFO:0007089': 'embryo',
        'EFO:0007116': 'embryo',
        'EFO:0005715': 'eye',
        'EFO:0001182': 'kidney',
        'EFO:0002179': 'kidney',
        'EFO:0005481': 'kidney',
        'EFO:0005707': 'kidney',
        'EFO:0001099': 'large intestine',
        'EFO:0001193': 'large intestine',
        'EFO:0001232': 'large intestine',
        'EFO:0006639': 'large intestine',
        'EFO:0001187': 'liver',
        'EFO:0001086': 'lung',
        'EFO:0001260': 'lung',
        'EFO:0002285': 'lung',
        'EFO:0005233': 'lymph node',
        'EFO:0005285': 'lymph node',
        'EFO:0005333': 'lymph node',
        'EFO:0005334': 'lymph node',
        'EFO:0005335': 'lymph node',
        'EFO:0005337': 'lymph node',
        'EFO:0005338': 'lymph node',
        'EFO:0005339': 'lymph node',
        'EFO:0005340': 'lymph node',
        'EFO:0005341': 'lymph node',
        'EFO:0005342': 'lymph node',
        'EFO:0005343': 'lymph node',
        'EFO:0005344': 'lymph node',
        'EFO:0005345': 'lymph node',
        'EFO:0005346': 'lymph node',
        'EFO:0005352': 'lymph node',
        'EFO:0005353': 'lymph node',
        'EFO:0005482': 'lymph node',
        'EFO:0005724': 'lymph node',
        'EFO:0006283': 'lymph node',
        'EFO:0007074': 'lymph node',
        'EFO:0007112': 'lymph node',
        'EFO:0001203': 'mammary gland',
        'EFO:0001247': 'mammary gland',
        'EFO:0007070': 'mouth',
        'EFO:0007748': 'penis',
        'EFO:0007749': 'penis',
        'EFO:0007750': 'penis',
        'EFO:0002074': 'prostate gland',
        'EFO:0002095': 'prostate gland',
        'EFO:0002323': 'prostate gland',
        'EFO:0005726': 'prostate gland',
        'EFO:0006365': 'prostate gland',
        'EFO:0007610': 'prostate gland',
        'EFO:0007752': 'prostate gland',
        'EFO:0002103': 'skin of body',
        'EFO:0005712': 'skin of body',
        'EFO:0005720': 'skin of body',
        'EFO:0007099': 'skin of body',
        'EFO:0007102': 'skin of body',
        'EFO:0007105': 'skin of body',
        'EFO:0007106': 'skin of body',
        'EFO:0007107': 'skin of body',
        'EFO:0007108': 'skin of body',
        'EFO:0005909': 'skin of body',
        'EFO:0005236': 'testis',
        'EFO:0005718': 'uterus',
        'EFO:0005023': 'adipose tissue',
        'EFO:0003037': 'blood',
        'EFO:0002783': 'blood',
        'EFO:0001159': 'blood',
        'EFO:0001160': 'blood',
        'EFO:0001161': 'blood',
        'EFO:0001162': 'blood',
        'EFO:0002784': 'blood',
        'EFO:0002785': 'blood',
        'EFO:0002786': 'blood',
        'EFO:0002788': 'blood',
        'EFO:0002789': 'blood',
        'EFO:0002790': 'blood',
        'EFO:0007598': 'blood',
        'EFO:0002793': 'blood',
        'EFO:0002067': 'blood',
        'EFO:0005903': 'blood',
        'EFO:0002798': 'blood',
        'EFO:0002322': 'blood',
        'EFO:0002860': 'brain',
        'EFO:0002713': 'pancreas',
        'EFO:0001098': 'musculature of body',
        'EFO:0003044': 'lung',
        'EFO:0002847': 'lung',
        'EFO:0002150': 'kidney',
        'EFO:0002816': 'embryo',
        'EFO:0005901': 'embryo',
        'EFO:0005904': 'embryo',
        'EFO:0001222': 'embryo',
        'EFO:0002059': 'connective tissue',
        'EFO:0000586': 'connective tissue',
        'EFO:0005282': 'bone element',
        'EFO:0005283': 'bone element',
        'NTR:0003860': 'blood'
    }

}

preferred_name = {
    "OBI:0000626": "WGS",
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

# Note this also shows the final datastructure for ontology.json
ntr_assays = {
    "NTR:0003660": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "microRNA counts",
        "objectives": [],
        "organs": [],
        "preferred_name": "",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0000612": {
        "assay": ['RNA binding'],
        "category": [],
        "developmental": [],
        "name": "Switchgear",
        "objectives": [],
        "organs": [],
        "preferred_name": "",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0000762": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "shRNA knockdown followed by RNA-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "shRNA RNA-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0000763": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "siRNA knockdown followed by RNA-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "siRNA RNA-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0001132": {
        "assay": ['RNA binding'],
        "category": [],
        "developmental": [],
        "name": "RNA Bind-N-Seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "RNA Bind-N-Seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0003082": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "single cell isolation followed by RNA-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "single cell RNA-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0004774": {
        "assay": ['DNA accessibility'],
        "category": [],
        "developmental": [],
        "name": "genetic modification followed by DNase-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "genetic modification DNase-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0003814": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "CRISPR genome editing followed by RNA-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "CRISPR RNA-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0004619": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "CRISPRi followed by RNA-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "CRISPRi RNA-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0004875": {
        "assay": ['Genotyping'],
        "category": [],
        "developmental": [],
        "name": "genotype phasing by HiC",
        "objectives": [],
        "organs": [],
        "preferred_name": "genotyping HiC",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0004739": {
        "assay": ['Transcription'],
        "category": [],
        "developmental": [],
        "name": "BruUV-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "BruUV-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0005023": {
        "assay": ['DNA sequencing'],
        "category": [],
        "developmental": [],
        "name": "Circulome-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "Circulome-seq",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    },
    "NTR:0005141": {
        "assay": ['DNA binding'],
        "category": [],
        "developmental": [],
        "name": "Mint-ChIP-seq",
        "objectives": [],
        "organs": [],
        "preferred_name": "Mint-ChIP",
        "slims": [],
        "synonyms": [],
        "systems": [],
        "types": []
    }
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
                raise exceptions.Error("Could not parse the file! Is it a valid RDF/OWL ontology?")
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
            for o in self.rdfGraph.objects(anEntity, EFO_Synonym):
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
            slims = [shim]
    return slims


def getTermStructure():
    return {
        'id': '',
        'name': '',
        'preferred_name': '',
        'parents': [],
        'part_of': [],
        'has_part': [],
        'develops_from': [],
        'achieves_planned_objective': [],
        'organs': [],
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
    ''' Downloads UBERON, EFO and OBI ontologies and create a JSON file '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Get Uberon, EFO and OBI ontologies and generate the JSON file", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--uberon-url', help="Uberon version URL")
    parser.add_argument('--efo-url', help="EFO version URL")
    parser.add_argument('--obi-url', help="OBI version URL")
    args = parser.parse_args()

    uberon_url = args.uberon_url
    efo_url = args.efo_url
    obi_url = args.obi_url
    urls = [obi_url, uberon_url, efo_url]

    terms = {}
    for url in urls:
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
    for term in terms:
        terms[term]['data'] = list(set(terms[term]['parents']) | set(terms[term]['part_of']) | set(terms[term]['achieves_planned_objective']))
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
    with open('ontology.json', 'w') as outfile:
        json.dump(terms, outfile)


if __name__ == '__main__':
    main()
