from rdflib import ConjunctiveGraph, exceptions, Namespace
from rdflib import RDFS, RDF, BNode
from rdflib.collection import Collection
from .ntr_terms import (
    ntr_biosamples
)
from .manual_slims import slim_shims
import json

EPILOG = __doc__

OWLNS = Namespace("http://www.w3.org/2002/07/owl#")
OBO_OWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")

Synonym = OBO_OWL["hasExactSynonym"]
Ontology = OWLNS["Ontology"]
Class = OWLNS["Class"]
Thing = OWLNS["Thing"]
OnProperty = OWLNS["onProperty"]
SomeValuesFrom = OWLNS["someValuesFrom"]
IntersectionOf = OWLNS["intersectionOf"]

PART_OF = "http://purl.obolibrary.org/obo/BFO_0000050"
DERIVES_FROM = "http://www.obofoundry.org/ro/ro.owl#derives_from"
DEFAULT_LANGUAGE = "en"


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
                raise exceptions.Error(
                    "Could not parse the file! Is `%s` a valid RDF/OWL ontology?" % uri)
        finally:
            self.baseURI = self.get_OntologyURI() or uri
            self.allclasses = self.__getAllClasses(
                includeDomainRange=True, includeImplicit=True, removeBlankNodes=False, excludeRDF_OWL=False)

    def get_OntologyURI(self, return_as_string=True):
        test = [x for x, y, z in self.rdfGraph.triples(
            (None, RDF.type, Ontology))]
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

    # methods for getting ancestors and descendants of classes: by default, we do not include blank nodes
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

    def entitySynonyms(self, anEntity, getall=True):
        temp = []
        for o in self.rdfGraph.objects(anEntity, Synonym):
            temp += [o]
        return temp

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


def iterativeChildren(nodes, terms):
    data = 'data'
    results = []
    while 1:
        newNodes = []
        if len(nodes) == 0:
            break
        for node in nodes:
            results.append(node)
            if node in terms.keys():
                if terms[node][data]:
                    for child in terms[node][data]:
                        if child not in results:
                            newNodes.append(child)
        nodes = list(set(newNodes))
    return list(set(results))


def getTermStructure():
    return {
        'id': '',
        'name': '',
        'parents': [],
        'part_of': [],
        'derives_from': [],
        'ancestors': [],
        'data': [],
        'synonyms': []
    }


def main():
    ''' Downloads UBERON and EFO ontologies and create a JSON file '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Get Uberon, EFO, and MONDO ontologies and generate the JSON file", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--uberon-url', help="Uberon version URL")
    parser.add_argument('--efo-url', help="EFO version URL")
    parser.add_argument('--mondo-url', help="MONDO version URL")
    parser.add_argument('--hancestro-url', help="HANCESTRO version URL")
    args = parser.parse_args()

    uberon_url = args.uberon_url
    efo_url = args.efo_url
    mondo_url = args.mondo_url
    hancestro_url = args.hancestro_url
    url_whitelist = {
        uberon_url: ['UBERON', 'CL'],
        efo_url: ['EFO'],
        mondo_url: ['MONDO'],
        hancestro_url: ['HANCESTRO']
        }

    terms = {}
    # Run on ontologies defined in whitelist
    for url in url_whitelist.keys():
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
                            if PART_OF in col_list:
                                for subC in data.rdfGraph.objects(c, RDFS.subClassOf):
                                    term_id = splitNameFromNamespace(
                                        collection[0])[0].replace('_', ':')
                                    if term_id.split(':')[0] in url_whitelist[url]:
                                        if term_id not in terms:
                                            terms[term_id] = getTermStructure()
                                        terms[term_id]['part_of'].append(
                                            splitNameFromNamespace(subC)[0].replace('_', ':'))
            else:
                term_id = splitNameFromNamespace(c)[0].replace('_', ':')
                if term_id.split(':')[0] in url_whitelist[url]:
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
                                            terms[term_id]['part_of'].append(
                                                splitNameFromNamespace(o1)[0].replace('_', ':'))
                                elif o.__str__() == DERIVES_FROM:
                                    for o1 in data.rdfGraph.objects(parent, SomeValuesFrom):
                                        if not isBlankNode(o1):
                                            terms[term_id]['derives_from'].append(
                                                splitNameFromNamespace(o1)[0].replace('_', ':'))
                                        else:
                                            for o2 in data.rdfGraph.objects(o1, IntersectionOf):
                                                for o3 in data.rdfGraph.objects(o2, RDF.first):
                                                    if not isBlankNode(o3):
                                                        terms[term_id]['derives_from'].append(
                                                            splitNameFromNamespace(o3)[0].replace('_', ':'))
                                                for o3 in data.rdfGraph.objects(o2, RDF.rest):
                                                    for o4 in data.rdfGraph.objects(o3, RDF.first):
                                                        for o5 in data.rdfGraph.objects(o4, SomeValuesFrom):
                                                            for o6 in data.rdfGraph.objects(o5, IntersectionOf):
                                                                for o7 in data.rdfGraph.objects(o6, RDF.first):
                                                                    if not isBlankNode(o7):
                                                                        terms[term_id]['derives_from'].append(
                                                                            splitNameFromNamespace(o7)[0].replace('_', ':'))
                                                                        for o8 in data.rdfGraph.objects(o6, RDF.rest):
                                                                            for o9 in data.rdfGraph.objects(o8, RDF.first):
                                                                                if not isBlankNode(o9):
                                                                                    terms[term_id]['derives_from'].append(
                                                                                        splitNameFromNamespace(o9)[0].replace('_', ':'))
                        else:
                            terms[term_id]['parents'].append(
                                splitNameFromNamespace(parent)[0].replace('_', ':'))

                    for syn in data.entitySynonyms(c):
                        try:
                            terms[term_id]['synonyms'].append(syn.__str__())
                        except:
                            pass
    for term in terms:
        terms[term]['data'] = list(set(terms[term]['parents']) | set(terms[term]['part_of']) | set(
            terms[term]['derives_from']))

    for term in terms:
        ont_whitelist = [i for sublist in url_whitelist.values() for i in sublist]
        d = iterativeChildren(
            terms[term]['data'], terms)
        for dd in d:
            if dd.split(':')[0] in ont_whitelist:
                terms[term]['ancestors'].append(dd)

        terms[term]['ancestors'].append(term)

    for term in terms:
        del terms[term]['parents'], terms[term]['derives_from']
        del terms[term]['part_of'], terms[term]['id'], terms[term]['data']

    for ntr in ntr_biosamples:
        ancestors = set()
        for parent in ntr.get('child_of'):
            ancestors.update(terms[parent]['ancestors'])
        terms[ntr['term_id']] = {
            'name': ntr['name'],
            'synonyms': ntr['synonyms'],
            'ancestors': list(ancestors)
        }

    with open('ontology.json', 'w') as outfile:
        json.dump(terms, outfile)


if __name__ == '__main__':
    main()
