from snovault import (
    AuditFailure,
    audit_checker,
)


# flag biosamples that contain GM that is different from the GM in donor. It could be legitimate case, but we would like to see it.
# flag biosamples that have a GM that was specified in donor detecting redundant GM
def audit_biosample_modifications(value, system):
    
    if value['biosample_type'] == 'whole organisms':
        model_modifications_present = True
        model_modifications_ids = set()
        modifications_ids = set()
        if 'model_organism_donor_modifications' in value:
            for model_modification in value['model_organism_donor_modifications']:
                model_modifications_ids.add(model_modification)
        else:
            model_modifications_present = False
        if 'genetic_modifications' in value:
            for modification in value['genetic_modifications']:
                modifications_ids.add(modification)

        modification_difference = model_modifications_ids - modifications_ids
        if modification_difference and model_modifications_present:
            detail = 'Biosample {} '.format(value['@id']) + \
                     'contains genetic modifications {} that '.format(modification_difference) + \
                     'are not present in the list of genetic modifications {} '.format(
                         model_modifications_ids) + \
                     'of the corresponding strain.'            
            yield AuditFailure('mismatched genetic modifications', detail,
                               level='INTERNAL_ACTION')
        modification_duplicates = model_modifications_ids & modifications_ids
        if modification_duplicates:
            detail = 'Biosample {} '.format(value['@id']) + \
                     'contains genetic modifications {} that '.format(modification_duplicates) + \
                     'are duplicates of genetic modifications {} '.format(
                         model_modifications_ids) + \
                     'of the corresponding strain.'            
            yield AuditFailure('duplicated genetic modifications', detail,
                               level='INTERNAL_ACTION')
    return

# def audit_biosample_gtex_children(value, system):
# https://encodedcc.atlassian.net/browse/ENCD-3538


def audit_biosample_term(value, system):
    '''
    Biosample_term_id and biosample_term_name
    and biosample_type should all be present.
    This should be handled by schemas.
    Biosample_term_id should be in the ontology.
    Biosample_term_name should match biosample_term_id.
    '''

    if value['status'] in ['deleted']:
        return

    ontology = system['registry']['ontology']
    term_id = value['biosample_term_id']
    term_name = value.get('biosample_term_name')

    if term_id.startswith('NTR:'):
        detail = 'Biosample {} has a New Term Request {} - {}'.format(
            value['@id'],
            term_id,
            term_name)
        yield AuditFailure('NTR biosample', detail, level='INTERNAL_ACTION')
        return

    #  biosample term_type and term_name consistency moved to schema, release 56

    if term_id not in ontology:
        detail = 'Biosample {} has biosample_term_id of {} which is not in ontology'.format(
            value['@id'],
            term_id)
        yield AuditFailure('term_id not in ontology', term_id, level='INTERNAL_ACTION')
        return

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = 'Biosample {} has '.format(value['@id']) + \
                 'a mismatch between biosample term_id ({}) '.format(term_id) + \
                 'and term_name ({}), ontology term_name for term_id {} '.format(
                     term_name, term_id) + \
                 'is {}.'.format(ontology_term_name)
        yield AuditFailure('inconsistent ontology term', detail, level='ERROR')
        return


def audit_biosample_culture_date(value, system):
    '''
    A culture_harvest_date should not precede
    a culture_start_date.
    This should move to the schema.
    '''

    if value['status'] in ['deleted']:
        return

    if ('culture_start_date' not in value) or ('culture_harvest_date' not in value):
        return

    if value['culture_harvest_date'] <= value['culture_start_date']:
        detail = 'Biosample {} has a culture_harvest_date {} which precedes the culture_start_date {}'.format(
            value['@id'],
            value['culture_harvest_date'],
            value['culture_start_date'])
        yield AuditFailure('invalid dates', detail, level='ERROR')


def audit_biosample_donor(value, system):
    '''
    A biosample should have a donor.
    The organism of donor and biosample should match.
    '''
    if value['status'] in ['deleted']:
        return

    if 'donor' not in value:
        detail = 'Biosample {} is not associated with any donor.'.format(value['@id'])
        if 'award' in value and 'rfa' in value['award'] and \
           value['award']['rfa'] == 'GGR':
            yield AuditFailure('missing donor', detail, level='INTERNAL_ACTION')
            return
        else:
            yield AuditFailure('missing donor', detail, level='ERROR')
            return

    donor = value['donor']
    if value.get('organism') != donor.get('organism'):
        detail = 'Biosample {} is organism {}, yet its donor {} is organism {}. Biosamples require a donor of the same species'.format(
            value['@id'],
            value.get('organism'),
            donor['@id'],
            donor.get('organism'))
        yield AuditFailure('inconsistent organism', detail, level='ERROR')

    if 'mutated_gene' not in donor:
        return

    if value.get('organism') != donor['mutated_gene'].get('organism'):
        detail = 'Biosample {} is organism {}, but its donor {} mutated_gene is in {}. Donor mutated_gene should be of the same species as the donor and biosample'.format(
            value['@id'],
            value.get('organism'),
            donor['@id'],
            donor['mutated_gene'].get('organism'))
        yield AuditFailure('inconsistent mutated_gene organism', detail, level='ERROR')

    for i in donor['mutated_gene'].get('investigated_as'):
        if i in ['histone modification',
                 'tag',
                 'control',
                 'recombinant protein',
                 'nucleotide modification',
                 'other post-translational modification']:
            detail = 'Donor {} has an invalid mutated_gene {}. Donor mutated_genes should not be tags, controls, recombinant proteins or modifications'.format(
                donor['@id'],
                donor['mutated_gene'].get('name'))
            yield AuditFailure('invalid donor mutated_gene', detail, level='ERROR')


def audit_biosample_part_of_consistency(value, system):
    if 'part_of' not in value:
        return
    else:
        part_of_biosample = value['part_of']
        term_id = value['biosample_term_id']
        part_of_term_id = part_of_biosample['biosample_term_id']

        if 'biosample_term_name' in value:
            term_name = value['biosample_term_name']
        else:
            term_name = term_id
        if 'biosample_term_name' in part_of_biosample:
            part_of_term_name = part_of_biosample['biosample_term_name']
        else:
            part_of_term_name = part_of_term_id

        if term_id == part_of_term_id or part_of_term_id == 'UBERON:0000468':
            return

        ontology = system['registry']['ontology']
        if (term_id in ontology) and (part_of_term_id in ontology):
            if is_part_of(term_id, part_of_term_id, ontology) is True:
                return

        detail = 'Biosample {} '.format(value['@id']) + \
                 'with biosample term {} '.format(term_name) + \
                 'was separated from biosample {} '.format(part_of_biosample['@id']) + \
                 'with biosample term {}. '.format(part_of_term_name) + \
                 'The {} '.format(term_id) + \
                 'ontology does not note that part_of relationship.'
        yield AuditFailure('inconsistent biosample_term_id', detail,
                           level='INTERNAL_ACTION')
        return

# utility functions

def is_part_of(term_id, part_of_term_id, ontology):
    if 'part_of' not in ontology[term_id] or ontology[term_id]['part_of'] == []:
        return False
    if part_of_term_id in ontology[term_id]['part_of']:
        return True
    else:
        parents = []
        for x in ontology[term_id]['part_of']:
            parents.append(is_part_of(x, part_of_term_id, ontology))
        return any(parents)


function_dispatcher = {
    'audit_constructs': audit_biosample_constructs,
    'audit_bio_term': audit_biosample_term,
    'audit_culture_date': audit_biosample_culture_date,
    'audit_donor': audit_biosample_donor,
    'audit_part_of': audit_biosample_part_of_consistency
}

@audit_checker('Biosample',
               frame=['award',
                      'donor',
                      'donor.mutated_gene',
                      'part_of'])
def audit_biosample(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
