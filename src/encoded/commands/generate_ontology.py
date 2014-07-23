from rdflib import ConjunctiveGraph, exceptions, Namespace
from rdflib import RDFS, RDF, BNode
from rdflib.collection import Collection
import json

EPILOG = __doc__

OWLNS = Namespace("http://www.w3.org/2002/07/owl#")
OBO_OWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")
EFO = Namespace("http://www.ebi.ac.uk/efo/")

EFO_Synonym = EFO["alternative_term"]
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
    'UBERON:0001173': 'billary tree',
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
    'UBERON:0001043': 'esophagus',
    'UBERON:0001255': 'urinary bladder',
    'UBERON:0001264': 'pancreas',
    'UBERON:0001474': 'bone element',
    'UBERON:0002003': 'peripheral nerve',
    'UBERON:0002048': 'lung',
    'UBERON:0002097': 'skin of body',
    'UBERON:0002107': 'liver',
    'UBERON:0000059': 'large intestine',
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
    'UBERON:0002391': 'lymph',
    'UBERON:0010133': 'neuroendocrine gland',
    'UBERON:0001132': 'parathyroid gland',
    'UBERON:0002046': 'thyroid gland',
    'UBERON:0001981': 'blood vessel',
    'UBERON:0001473': 'lymphatic vessel',
    'UBERON:0000178': 'blood',
    'UBERON:0002268': 'olfactory organ',
    'UBERON:0007844': 'cartilage element',
    'UBERON:0001690': 'ear',
    'UBERON:0001987': 'placenta',
    'UBERON:0001911': 'mammary gland',
    'UBERON:0001630': 'muscle organ',
    'UBERON:0000007': 'pituitary gland',
    'UBERON:0002370': 'thymus',
    'UBERON:0000478': 'extraembryonic structure'
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
        print "Error in <sort_uri_list_by_name>: possibly a UnicodeEncodeError"
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
    slimTerms = []
    if slimType == 'developmental':
        slimTerms = developental_slims
    elif slimType == 'organ':
        slimTerms = organ_slims
    elif slimType == 'system':
        slimTerms = system_slims
    for slimTerm in slimTerms:
        if slimType == 'developmental':
            if slimTerm in terms[goid]['closure_with_develops_from']:
                slims.append(slimTerms[slimTerm])
        else:
            if slimTerm in terms[goid]['closure']:
                slims.append(slimTerms[slimTerm])
    return slims


def getTermStructure():
    return {
        'id': '',
        'name': '',
        'parents': [],
        'part_of': [],
        'develops_from': [],
        'organs': [],
        'closure': [],
        'slims': [],
        'data': [],
        'closure_with_develops_from': [],
        'data_with_develops_from': [],
        'synonyms': []
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
                    else:
                        terms[term_id]['parents'].append(splitNameFromNamespace(parent)[0].replace('_', ':'))
                
                for syn in data.entitySynonyms(c):
                    try:
                        terms[term_id]['synonyms'].append(syn.__str__())
                    except:
                        pass
    for term in terms:
        terms[term]['data'] = list(set(terms[term]['parents']) | set(terms[term]['part_of']))
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
        del terms[term]['closure'], terms[term]['closure_with_develops_from']

    for term in terms:
        del terms[term]['parents'], terms[term]['part_of'], terms[term]['develops_from']
        del terms[term]['id'], terms[term]['data'], terms[term]['data_with_develops_from']

    with open('ontology.json', 'w') as outfile:
        json.dump(terms, outfile)


if __name__ == '__main__':
    main()
