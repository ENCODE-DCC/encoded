from snovault import (
    AuditFailure,
    audit_checker,
)

from .ontology_data import biosampleType_ontologyPrefix
from .gtex_data import gtexDonorsList
from .gtex_data import gtexParentsList



term_mapping = {
    "head": "UBERON:0000033",
    "limb": "UBERON:0002101",
    "salivary gland": "UBERON:0001044",
    "male accessory sex gland": "UBERON:0010147",
    "testis": "UBERON:0000473",
    "female gonad": "UBERON:0000992",
    "digestive system": "UBERON:0001007",
    "arthropod fat body": "UBERON:0003917",
    "antenna": "UBERON:0000972",
    "adult maxillary segment": "FBbt:00003016",
    "female reproductive system": "UBERON:0000474",
    "male reproductive system": "UBERON:0000079",
    "nucleus": "GO:0005634",
    "cytosol": "GO:0005829",
    "chromatin": "GO:0000785",
    "membrane": "GO:0016020",
    "mitochondria": "GO:0005739",
    "nuclear matrix": "GO:0016363",
    "nucleolus": "GO:0005730",
    "nucleoplasm": "GO:0005654",
    "polysome": "GO:0005844",
    "insoluble cytoplasmic fraction": "NTR:0002594"
}

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
                                   level='DCC_ACTION')
                return

        if len(constructs_ids) > 0:
            for c in constructs_ids:
                if c not in model_constructs_ids:
                    yield AuditFailure('mismatched constructs', detail,
                                       level='DCC_ACTION')
                    return


@audit_checker('biosample', frame=['organism'])
def audit_biosample_human_no_model_organism_properties(value, system):
    '''
    human bioamples shouldn't have model organism properties initiated
    '''
    if 'organism' not in value:
        return

    if value['organism']['scientific_name'] != 'Homo sapiens':
        return
    terms_list = []
    for term in model_organism_terms:
        if term in value:
            terms_list.append(term)
    if len(terms_list) == 1:
        detail = 'Human biosample {}'.format(value['@id']) + \
                 ' contains model organism fileld {}'.format(terms_list[0])
        yield AuditFailure('model organism term in human biosample', detail,
                           level='ERROR')
        return
    if len(terms_list) > 1:
        detail = 'Human biosample {}'.format(value['@id']) + \
                 ' contains model organism filelds {}'.format(terms_list)
        yield AuditFailure('model organism term in human biosample', detail,
                           level='ERROR')
        return


@audit_checker('biosample', frame=['source', 'part_of', 'donor'])
def audit_biosample_gtex_children(value, system):
    '''
    GTEX children biosamples have to be properly registered.
    - aliases (column A from plate-maps)
    - part_of pointing to the parent biosample
    - source Kristin Ardlie
    '''
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'donor' not in value:
        return
    if (value['donor']['accession'] in gtexDonorsList) and \
       (value['accession'] not in gtexParentsList):
        if 'source' not in value:
            detail = 'GTEX biosample {} has no source'.format(
                value['@id'])
            yield AuditFailure('GTEX biosample missing source', detail, level='DCC_ACTION')
        else:
            if (value['source']['uuid'] != 'f85ecd67-abf2-4a26-89c8-53a7273c8b0c'):
                detail = 'GTEX biosample {} has incorrect source {}'.format(
                    value['@id'],
                    value['source']['title'])
                yield AuditFailure('GTEX biosample incorrect source', detail, level='DCC_ACTION')
        if 'part_of' not in value:
            detail = 'GTEX child biosample {} is not asociated with any parent biosample'.format(
                value['@id'])
            yield AuditFailure('GTEX biosample missing part_of property', detail,
                               level='DCC_ACTION')
        else:
            partOfBiosample = value['part_of']
            if (partOfBiosample['accession'] not in gtexParentsList):
                detail = 'GTEX child biosample {} is asociated '.format(value['@id']) + \
                         'with biosample {} which is '.format(partOfBiosample['@id']) + \
                         'not a part of parent biosamples list'
                yield AuditFailure('GTEX biosample invalid part_of property', detail,
                                   level='DCC_ACTION')
            else:
                if value['biosample_term_id'] != partOfBiosample['biosample_term_id']:
                    detail = 'GTEX child biosample {} is associated with '.format(value['@id']) + \
                             'biosample {} that has a different '.format(partOfBiosample['@id']) + \
                             'biosample_term_id {}'.format(partOfBiosample['biosample_term_id'])
                    yield AuditFailure('GTEX biosample invalid part_of property', detail,
                                       level='DCC_ACTION')
        if ('aliases' not in value):
            detail = 'GTEX biosample {} has no aliases'.format(value['@id'])
            yield AuditFailure('GTEX biosample missing aliases', detail, level='DCC_ACTION')
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
                                   level='DCC_ACTION')
    return


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
        yield AuditFailure('NTR biosample', detail, level='DCC_ACTION')
        return

    biosample_prefix = term_id.split(':')[0]
    if biosample_prefix not in biosampleType_ontologyPrefix[value['biosample_type']]:
        detail = 'Biosample {} of '.format(value['@id']) + \
                 'type {} '.format(value['biosample_type']) + \
                 'has biosample_term_id {} '.format(value['biosample_term_id']) + \
                 'that is not one of ' + \
                 '{}'.format(biosampleType_ontologyPrefix[value['biosample_type']])
        yield AuditFailure('biosample term-type mismatch', detail, level='DCC_ACTION')
        return

    if term_id not in ontology:
        detail = 'Biosample {} has biosample_term_id of {} which is not in ontology'.format(
            value['@id'],
            term_id)
        yield AuditFailure('term_id not in ontology', term_id, level='DCC_ACTION')
        return

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = 'Biosample {} has '.format(value['@id']) + \
                 'a mismatch between biosample_term_id {} '.format(term_id) + \
                 'and biosample_term_name {}'.format(term_name)
        yield AuditFailure('mismatched ontology term', detail, level='ERROR')
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

@audit_checker('biosample', frame=['organism', 'donor', 'donor.organism', 'donor.mutated_gene', 'donor.mutated_gene.organism'])
def audit_biosample_donor(value, system):
    '''
    A biosample should have a donor.
    The organism of donor and biosample should match.
    Pooled_from biosamples do not need donors??
    '''
    if value['status'] in ['deleted']:
        return

    if ('donor' not in value) and (value['pooled_from']):
        return

    if ('donor' not in value) and (not value['pooled_from']):
        detail = 'Biosample {} requires a donor'.format(value['@id'])
        raise AuditFailure('missing donor', detail, level='ERROR')
        return

    donor = value['donor']
    if value['organism']['name'] != donor['organism']['name']:
        detail = 'Biosample {} is organism {}, yet its donor {} is organism {}. Biosamples require a donor of the same species'.format(
            value['@id'],
            value['organism']['name'],
            donor['@id'],
            donor['organism']['name'])
        raise AuditFailure('mismatched organism', detail, level='ERROR')

    if 'mutated_gene' not in donor:
        return

    if value['organism']['name'] != donor['mutated_gene']['organism']['name']:
        detail = 'Biosample {} is organism {}, but its donor {} mutated_gene is in {}. Donor mutated_gene should be of the same species as the donor and biosample'.format(
            value['@id'],
            value['organism']['name'],
            donor['@id'],
            donor['mutated_gene']['organism']['name'])
        raise AuditFailure('mismatched mutated_gene organism', detail, level='ERROR')

    for i in donor['mutated_gene']['investigated_as']:
        if i in ['histone modification', 'tag', 'control', 'recombinant protein', 'nucleotide modification', 'other post-translational modification']:
            detail = 'Donor {} has an invalid mutated_gene {}. Donor mutated_genes should not be tags, controls, recombinant proteins or modifications'.format(
                donor['@id'],
                donor['mutated_gene']['name'])
            raise AuditFailure('invalid donor mutated_gene', detail, level='ERROR')

@audit_checker('biosample', frame='object')
def audit_biosample_subcellular_term_match(value, system):
    '''
    The subcellular_fraction_term_name and subcellular_fraction_term_id
    should be concordant. This should be a calculated field
    If one exists the other should. This should be handled in the schema.
    '''
    if value['status'] in ['deleted']:
        return

    if ('subcellular_fraction_term_name' not in value) or ('subcellular_fraction_term_id' not in value):
        return

    expected_name = term_mapping[value['subcellular_fraction_term_name']]
    if expected_name != (value['subcellular_fraction_term_id']):
        detail = 'Biosample {} has a mismatch between subcellular_fraction_term_name "{}" and subcellular_fraction_term_id "{}"'.format(
            value['@id'],
            value['subcellular_fraction_term_name'],
            value['subcellular_fraction_term_id'])
        raise AuditFailure('mismatched subcellular_fraction_term', detail, level='ERROR')


@audit_checker('biosample', frame='object')
def audit_biosample_depleted_term_match(value, system):
    '''
    The depleted_in_term_name and depleted_in_term_name
    should be concordant. This should be a calcualted field.
    If one exists, the other should.  This should be handled in the schema.
    '''
    if value['status'] == 'deleted':
        return

    if 'depleted_in_term_name' not in value:
        return

    if len(value['depleted_in_term_name']) != len(value['depleted_in_term_id']):
        detail = 'Biosample {} has a depleted_in_term_name array and depleted_in_term_id array of differing lengths'.format(
            value['@id'])
        raise AuditFailure('mismatched depleted_in_term length', detail, level='ERROR')
        return

    for i, dep_term in enumerate(value['depleted_in_term_name']):
        if (term_mapping[dep_term]) != (value['depleted_in_term_id'][i]):
            detail = 'Biosample {} has a mismatch between {} and {}'.format(
                value['@id'],
                dep_term,
                value['depleted_in_term_id'][i])
            raise AuditFailure('mismatched depleted_in_term', detail, level='ERROR')


@audit_checker('biosample', frame='object')
def audit_biosample_transfection_type(value, system):
    '''
    A biosample with constructs or rnais should have a
    transfection_type
    '''
    if value['status'] == 'deleted':
        return

    if (value['rnais']) and ('transfection_type' not in value):
        detail = 'Biosample {} with a value for RNAi requires transfection_type'.format(value['@id'])
        raise AuditFailure('missing transfection_type', detail, level='ERROR')

    if (value['constructs']) and ('transfection_type' not in value):
        detail = 'Biosample {} with a value for construct requires transfection_type'.format(value['@id'])
        raise AuditFailure('missing transfection_type', detail, level='ERROR')


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


@audit_checker('biosample', frame=['part_of'])
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
                           level='DCC_ACTION')
        return
