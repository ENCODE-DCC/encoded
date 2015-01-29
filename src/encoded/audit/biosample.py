from ..auditor import (
    AuditFailure,
    audit_checker,
)


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
    "nucleus": "GO:0005634",
    "cytosol": "GO:0005829",
    "chromatin": "GO:0000785",
    "membrane": "GO:0016020",
    "mitochondria": "GO:0005739",
    "nuclear matrix": "GO:0016363",
    "nucleolus": "GO:0005730",
    "nucleoplasm": "GO:0005654",
    "polysome": "GO:0005844"
}


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
            value['accession'],
            term_id,
            term_name)
        raise AuditFailure('NTR biosample', detail, level='DCC_ACTION')

    if term_id not in ontology:
        detail = 'Biosample {} has biosample_term_id of {} which is not in ontology'.format(
            value['accession'],
            term_id)
        raise AuditFailure('term_id not in ontology', term_id, level='DCC_ACTION')

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = 'Biosample {} has a mismatch between biosample_term_id "{}" and biosample_term_name "{}"'.format(
            value['accession'],
            term_id,
            term_name,
            )
        raise AuditFailure('mismatched biosample_term', detail, level='DCC_ACTION')


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
            value['accession'],
            value['culture_harvest_date'],
            value['culture_start_date'])
        raise AuditFailure('invalid dates', detail, level='ERROR')


@audit_checker('biosample', frame=['organism', 'donor', 'donor.organism'])
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
        detail = 'Biosample {} requires a donor'.format(value['accession'])
        raise AuditFailure('missing donor', detail, level='ERROR')
        return

    donor = value['donor']
    if value['organism']['name'] != donor['organism']['name']:
        detail = 'Biosample {} is organism {}, yet its donor {} is organism {}. Biosamples require a donor of the same species'.format(
            value['accession'],
            value['organism']['name'],
            donor['accession'],
            donor['organism']['name'])
        raise AuditFailure('mismatched organism', detail, level='ERROR')


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
            value['accession'],
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
            value['accession'])
        raise AuditFailure('mismatched depleted_in_term length', detail, level='ERROR')
        return

    for i, dep_term in enumerate(value['depleted_in_term_name']):
        if (term_mapping[dep_term]) != (value['depleted_in_term_id'][i]):
            detail = 'Biosample {} has a mismatch between {} and {}'.format(
                value['accession'],
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
        detail = 'Biosample {} with a value for RNAi requires transfection_type'.format(value['accession'])
        raise AuditFailure('missing transfection_type', detail, level='ERROR')

    if (value['constructs']) and ('transfection_type' not in value):
        detail = 'Biosample {} with a value for construct requires transfection_type'.format(value['accession'])
        raise AuditFailure('missing transfection_type', detail, level='ERROR')
