import json
from urllib2 import Request, urlopen

EPILOG = __doc__


def getTerm(stream):
    ''' Get GO term block from the obo file'''

    block = []
    for line in stream:
        if line.strip() == "[Term]" or line.strip() == "[Typedef]":
            break
        else:
            if line.strip() != "":
                block.append(line.strip())

    return block


def parseTagValue(term):
    ''' Get tag-value pairs of each GO Term '''

    data = {}
    for line in term:
        tag = line.split(': ', 1)[0]
        value = line.split(': ', 1)[1]
        if not tag in data:
            data[tag] = []
        data[tag].append(value)

    return data


def getDescendents(goid):
    ''' Get Descendents of Go Term '''

    recursiveArray = [goid]
    if goid in terms:
        children = terms[goid]['children']
        if len(children) > 0:
            for child in children:
                recursiveArray.extend(getDescendents(child))

    return set(recursiveArray)


def getAncestors(goid):
    ''' Get Ancestors of GO ID '''

    recursiveArray = [goid]
    if goid in terms:
        parents = terms[goid]['parents']
        if len(parents) > 0:
            for parent in parents:
                recursiveArray.extend(getAncestors(parent))

    return set(recursiveArray)


def iterativeChildren(nodes):
    results = []
    while 1:
        newNodes = []
        if len(nodes) == 0:
            break
        for node in nodes:
            results.append(node)
            if terms[node]['data']:
                for child in terms[node]['data']:
                    if child not in results:
                        newNodes.append(child)
        nodes = newNodes
    return results


def iterativeDev(nodes):
    results = []
    while 1:
        newNodes = []
        if len(nodes) == 0:
            break
        for node in nodes:
            results.append(node)
            if terms[node]['data_with_develops_from']:
                for child in terms[node]['data_with_develops_from']:
                    if child not in results:
                        newNodes.append(child)
        nodes = newNodes
    return results


def getDevelopmentSlims(goid):
    ''' Get Developmental Slims '''

    slims = []
    slimTerms = {
        'UBERON:0000926': 'mesoderm',
        'UBERON:0000924': 'ectoderm',
        'UBERON:0000925': 'endoderm'
    }
    for slimTerm in slimTerms:
        if slimTerm in terms[goid]['closure_with_develops_from']:
            slims.append(slimTerms[slimTerm])
    return slims


def getSystemSlims(goid):
    ''' Get System Slims '''

    slims = []
    slimTerms = {
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
    for slimTerm in slimTerms:
        if slimTerm in terms[goid]['closure']:
            slims.append(slimTerms[slimTerm])
    return slims


def getOrganSlims(goid):
    ''' Get Organ Slims '''

    slims = []
    slimTerms = {
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
    for slimTerm in slimTerms:
        if slimTerm in terms[goid]['closure']:
            slims.append(slimTerms[slimTerm])
    return slims

def getRoadmapSlims(goid):
    ''' Get Roadmap Slims '''

    slims = []
    slimTerms = {
        'UBERON:0002369': 'adrenal gland',
        'UBERON:0000178': 'blood',
        'UBERON:0002481': 'bone tissue',
        'UBERON:0000955': 'brain',
        'UBERON:0000310': 'breast',
        'UBERON:0000002': 'uterine cervix',
        'CL:0002322': 'embryonic stem cell',
        'UBERON:0001013': 'adipose tissue',
        'UBERON:0001155': 'colon',
        'UBERON:0002114': 'duodenum',
        'UBERON:0001043': 'esophagus',
        'UBERON:0000160': 'intestine',
        'UBERON:0001052': 'rectum',
        'UBERON:0000945': 'stomach',
        'UBERON:0000948': 'heart',
        'EFO:0004905': 'induced pluripotent stem cell',
        'UBERON:0002113': 'kidney',
        'UBERON:0002107': 'liver',
        'UBERON:0002048': 'lung',
        'UBERON0002385': 'muscle tissue',
        'UBERON:0002119': 'female gonad',
        'UBERON:0001264': 'pancreas',
        'UBERON:0001987': 'placenta',
        'UBERON:0002097': 'skin of body',
        'UBERON:0002106': 'spleen',
        'UBERON:0003891': 'stromal',
        'UBERON:0002370': 'thymus',
        'UBERON0002049': 'vasculature'
    }
    for slimTerm in slimTerms:
        if slimTerm in terms[goid]['closure']:
            slims.append(slimTerms[slimTerm])
    return slims


def getTermStructure():
    return {
        'id': '',
        'name': '',
        'parents': [],
        'children': [],
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


terms = {}


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate ontology JSON file", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--uberon-url', help="Uberon version URL")
    parser.add_argument('--efo-url', help="EFO version URL")
    args = parser.parse_args()

    term_prefixs = ['UBERON', 'CL', 'CHEBI', 'GO', 'IAO', 'PATO', 'PR', 'NCBITaxon', 'EFO', 'BFO']
    stupid_terms = []

    uberon_url = args.uberon_url
    efo_url = args.efo_url
    urls = [uberon_url, efo_url]
    for url in urls:
        req = Request(url)
        oboFile = urlopen(req)

        #skip the file header lines
        getTerm(oboFile)

        #infinite loop to go through the obo file.
        #Breaks when the term returned is empty, indicating end of file
        while 1:
            #get the term using the two parsing functions
            term = parseTagValue(getTerm(oboFile))
            if len(term) != 0:
                if (term['id'][0]).find(':') != -1:
                    if ((term['id'][0]).split(':'))[0] in term_prefixs:
                        try:
                            termID = term['id'][0]
                            termName = ''
                            try:
                                termName = term['name'][0]
                            except KeyError:
                                pass

                            if 'is_a' in term:
                                termParents = [p.split()[0] for p in term['is_a']]

                                if not termID in terms:
                                    terms[termID] = getTermStructure()

                                #append termID and termName to the dict
                                terms[termID]['id'] = termID
                                terms[termID]['name'] = termName

                                #for every parent term, add this current term as children
                                for termParent in termParents:
                                    if (termParent.split(':'))[0] in term_prefixs:
                                        if termParent != 'CL:0000812':
                                            terms[termID]['parents'].append(termParent)
                                            if not termParent in terms:
                                                terms[termParent] = {
                                                    'parents': [],
                                                    'children': [],
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
                                            terms[termParent]['children'].append(termID)

                                if 'relationship' in term:
                                    relations = [p.split()[0] for p in term['relationship']]
                                    relationTerms = [p.split()[1] for p in term['relationship']]
                                    relationCheck = []
                                    for p in term['relationship']:
                                        try:
                                            relationCheck.append(p.split()[2])
                                        except:
                                            relationCheck.append("N/A")
                                    count = 0
                                    relationships = ['part_of', 'develops_from']
                                    for relation in relations:
                                        if relation in relationships:
                                            if relationTerms[count] != 'CL:0000812':
                                                if ((relationTerms[count]).split(':'))[0] in term_prefixs:
                                                    if relationCheck[count] == '!' or 'NCBITaxon:9606' in relationCheck[count] or 'source' in relationCheck[count]:
                                                        terms[termID][relation].append(relationTerms[count])
                                        count = count + 1

                                if 'synonym' in term:
                                    for synonym in term['synonym']:
                                        if 'EXACT' in synonym:
                                            terms[termID]['synonyms'].append(synonym.split('"')[1])
                            else:
                                if term['id'][0] not in terms:
                                    terms[termID] = getTermStructure()
                                    #append termID and termName to the dict
                                    terms[termID]['id'] = termID
                                    terms[termID]['name'] = termName
                                else:
                                    terms[termID]['id'] = termID
                                    terms[termID]['name'] = termName
                        except KeyError:
                            stupid_terms.append(termID)
            else:
                break

    # Deleting all useless, time wasting terms
    for stupid_term in stupid_terms:
        try:
            del(terms[stupid_term])
        except KeyError:
            pass

    useless = []
    for term in terms:
        try:
            terms[term]['id']
        except:
            useless.append(term)

    for useL in useless:
        del(terms[useL])

    for term in terms:
        terms[term]['data'] = list(set(terms[term]['parents']) | set(terms[term]['part_of']))
        terms[term]['data_with_develops_from'] = list(set(terms[term]['data']) | set(terms[term]['develops_from']))

    for term in terms:
        words = iterativeChildren(terms[term]['data'])
        for word in words:
            terms[term]['closure'].append(word)

        d = iterativeDev(terms[term]['data_with_develops_from'])
        for dd in d:
            terms[term]['closure_with_develops_from'].append(dd)
        terms[term]['closure'] = list(set(terms[term]['closure']))
        terms[term]['closure'].append(term)
        terms[term]['closure_with_develops_from'] = list(set(terms[term]['closure_with_develops_from']))
        terms[term]['closure_with_develops_from'].append(term)

        terms[term]['systems'] = getSystemSlims(term)
        terms[term]['organs'] = getOrganSlims(term)
        terms[term]['developmental'] = getDevelopmentSlims(term)
        terms[term]['roadmap'] = getRoadmapSlims(term)

    for term in terms:
        del(terms[term]['parents'])
        del(terms[term]['children'])
        del(terms[term]['part_of'])
        del(terms[term]['develops_from'])
        del(terms[term]['id'])
        del(terms[term]['closure'])
        del(terms[term]['closure_with_develops_from'])
        del(terms[term]['data'])
        del(terms[term]['data_with_develops_from'])

    with open('ontology.json', 'w') as outfile:
        json.dump(terms, outfile)

if __name__ == '__main__':
    main()
