from snovault import (
    AuditFailure,
    audit_checker,
)

from .ontology_data import biosampleType_ontologyPrefix
from .gtex_data import gtexDonorsList
from .gtex_data import gtexParentsList


model_organism_terms = ['model_organism_mating_status',
                        'model_organism_sex',
                        'mouse_life_stage',
                        'fly_life_stage',
                        'fly_synchronization_stage',
                        'post_synchronization_time',
                        'post_synchronization_time_units',
                        'worm_life_stage',
                        'worm_synchronization_stage',
                        'model_organism_age',
                        'model_organism_age_units',
                        'model_organism_health_status',
                        'model_organism_donor_constructs']


@audit_checker('biosample', frame=['constructs', 'model_organism_donor_constructs'])
def audit_biosample_constructs(value, system):

    if value['biosample_type'] == 'whole organisms':
        model_constructs_present = True
        model_constructs_ids = set()
        constructs_ids = set()
        if 'model_organism_donor_constructs' in value:
            for model_construct in value['model_organism_donor_constructs']:
                model_constructs_ids.add(model_construct['@id'])
        else:
            model_constructs_present = False
        if 'constructs' in value:
            for construct in value['constructs']:
                constructs_ids.add(construct['@id'])

        detail = 'Biosample {} '.format(value['@id']) + \
                 'contains mismatched constructs {} and '.format(constructs_ids) + \
                 'model_organism_donor_constructs {}.'.format(
                 model_constructs_ids)

        if len(model_constructs_ids) != len(constructs_ids):
            if model_constructs_present is False:
                detail = 'Biosample {} '.format(value['@id']) + \
                         'contains constructs {} and '.format(constructs_ids) + \
                         'does not contain any model_organism_donor_constructs.'
                yield AuditFailure('mismatched constructs', detail,
                                   level='INTERNAL_ACTION')
                return

        if len(constructs_ids) > 0:
            for c in constructs_ids:
                if c not in model_constructs_ids:
                    yield AuditFailure('mismatched constructs', detail,
                                       level='INTERNAL_ACTION')
                    return

'''
@audit_checker('biosample', frame=['source', 'part_of', 'donor'])
def audit_biosample_gtex_children(value, system):
    #GTEX children biosamples have to be properly registered.
    #- aliases (column A from plate-maps)
    #- part_of pointing to the parent biosample
    #- source Kristin Ardlie
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'donor' not in value:
        return
    if (value['donor']['accession'] in gtexDonorsList) and \
       (value['accession'] not in gtexParentsList):
        if 'source' not in value:
            detail = 'GTEX biosample {} has no source'.format(
                value['@id'])
            yield AuditFailure('GTEX biosample missing source', detail, level='INTERNAL_ACTION')
        else:
            if (value['source']['uuid'] != 'f85ecd67-abf2-4a26-89c8-53a7273c8b0c'):
                detail = 'GTEX biosample {} has incorrect source {}'.format(
                    value['@id'],
                    value['source']['title'])
                yield AuditFailure('GTEX biosample incorrect source', detail, level='INTERNAL_ACTION')
        if 'part_of' not in value:
            detail = 'GTEX child biosample {} is not asociated with any parent biosample'.format(
                value['@id'])
            yield AuditFailure('GTEX biosample missing part_of property', detail,
                               level='INTERNAL_ACTION')
        else:
            partOfBiosample = value['part_of']
            if (partOfBiosample['accession'] not in gtexParentsList):
                detail = 'GTEX child biosample {} is asociated '.format(value['@id']) + \
                         'with biosample {} which is '.format(partOfBiosample['@id']) + \
                         'not a part of parent biosamples list'
                yield AuditFailure('GTEX biosample invalid part_of property', detail,
                                   level='INTERNAL_ACTION')
            else:
                if value['biosample_term_id'] != partOfBiosample['biosample_term_id']:
                    detail = 'GTEX child biosample {} is associated with '.format(value['@id']) + \
                             'biosample {} that has a different '.format(partOfBiosample['@id']) + \
                             'biosample_term_id {}'.format(partOfBiosample['biosample_term_id'])
                    yield AuditFailure('GTEX biosample invalid part_of property', detail,
                                       level='INTERNAL_ACTION')
        if ('aliases' not in value):
            detail = 'GTEX biosample {} has no aliases'.format(value['@id'])
            yield AuditFailure('GTEX biosample missing aliases', detail, level='INTERNAL_ACTION')
        else:
            donorAliases = value['donor']['aliases']
            repDonorAlias = ''
            for da in donorAliases:
                if da[0:7] == 'gtex:PT':
                    repDonorAlias = 'gtex:ENC-'+da[8:13]
            childAliases = value['aliases']
            aliasFlag = False
            for ca in childAliases:
                if ca[0:14] == repDonorAlias:
                    aliasFlag = True
            if aliasFlag is False:
                detail = 'GTEX biosample {} aliases {} '.format(value['@id'],
                                                                childAliases) + \
                         'do not include an alias based on plate-map, column A identifier'
                yield AuditFailure('GTEX biosample missing aliases', detail,
                                   level='INTERNAL_ACTION')
    return
'''

@audit_checker('biosample', frame='object')
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

    if 'biosample_term_id' not in value:
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

    biosample_prefix = term_id.split(':')[0]
    if biosample_prefix not in biosampleType_ontologyPrefix[value['biosample_type']]:
        detail = 'Biosample {} of '.format(value['@id']) + \
                 'type {} '.format(value['biosample_type']) + \
                 'has biosample_term_id {} '.format(value['biosample_term_id']) + \
                 'that is not one of ' + \
                 '{}'.format(biosampleType_ontologyPrefix[value['biosample_type']])
        yield AuditFailure('biosample term-type mismatch', detail, level='INTERNAL_ACTION')
        return

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


@audit_checker('biosample', frame='object')
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
        raise AuditFailure('invalid dates', detail, level='ERROR')


@audit_checker('biosample', frame=[
    'award',
    'organism',
    'donor',
    'donor.organism',
    'donor.mutated_gene',
    'donor.mutated_gene.organism'])
def audit_biosample_donor(value, system):
    '''
    A biosample should have a donor.
    The organism of donor and biosample should match.
    '''
    if value['status'] in ['deleted']:
        return

    if ('donor' not in value):
        detail = 'Biosample {} is not associated with any donor.'.format(value['@id'])
        if 'award' in value and 'rfa' in value['award'] and \
           value['award']['rfa'] == 'GGR':
            raise AuditFailure('missing donor', detail, level='INTERNAL_ACTION')
            return
        else:
            raise AuditFailure('missing donor', detail, level='ERROR')
            return

    donor = value['donor']
    if value['organism']['name'] != donor['organism']['name']:
        detail = 'Biosample {} is organism {}, yet its donor {} is organism {}. Biosamples require a donor of the same species'.format(
            value['@id'],
            value['organism']['name'],
            donor['@id'],
            donor['organism']['name'])
        raise AuditFailure('inconsistent organism', detail, level='ERROR')

    if 'mutated_gene' not in donor:
        return

    if value['organism']['name'] != donor['mutated_gene']['organism']['name']:
        detail = 'Biosample {} is organism {}, but its donor {} mutated_gene is in {}. Donor mutated_gene should be of the same species as the donor and biosample'.format(
            value['@id'],
            value['organism']['name'],
            donor['@id'],
            donor['mutated_gene']['organism']['name'])
        raise AuditFailure('inconsistent mutated_gene organism', detail, level='ERROR')

    for i in donor['mutated_gene']['investigated_as']:
        if i in ['histone modification', 'tag', 'control', 'recombinant protein', 'nucleotide modification', 'other post-translational modification']:
            detail = 'Donor {} has an invalid mutated_gene {}. Donor mutated_genes should not be tags, controls, recombinant proteins or modifications'.format(
                donor['@id'],
                donor['mutated_gene']['name'])
            raise AuditFailure('invalid donor mutated_gene', detail, level='ERROR')


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


@audit_checker('biosample', frame=['originated_from'])
def audit_biosample_originated_from_consistency(value, system):
    if 'originated_from' not in value:
        return
    else:
        originated_from_biosample = value['originated_from']
        term_id = value['biosample_term_id']
        originated_from_term_id = originated_from_biosample['biosample_term_id']

        if 'biosample_term_name' in value:
            term_name = value['biosample_term_name']
        else:
            term_name = term_id
        if 'biosample_term_name' in originated_from_biosample:
            originated_from_term_name = originated_from_biosample['biosample_term_name']
        else:
            originated_from_term_name = originated_from_term_id

        if term_id == originated_from_term_id or originated_from_term_id == 'UBERON:0000468':
            return

        ontology = system['registry']['ontology']
        if (term_id in ontology) and (originated_from_term_id in ontology):
            if is_part_of(term_id, originated_from_term_id, ontology) is True:
                return

        detail = 'Biosample {} '.format(value['@id']) + \
                 'with biosample term {} '.format(term_name) + \
                 'was separated from biosample {} '.format(originated_from_biosample['@id']) + \
                 'with biosample term {}. '.format(originated_from_term_name) + \
                 'The {} '.format(term_id) + \
                 'ontology does not note that originated_from relationship.'
        yield AuditFailure('inconsistent biosample_term_id', detail,
                           level='INTERNAL_ACTION')
        return
