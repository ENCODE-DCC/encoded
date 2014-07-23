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


@audit_checker('biosample')
def audit_biosample_term(value, system):
    if value['status'] == 'deleted':
        return

    if 'biosample_term_id' not in value:
        return
    ontology = system['registry']['ontology']
    term_id = value['biosample_term_id']
    term_name = value.get('biosample_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        raise AuditFailure('NTR', detail, level='WARNING')

    if term_id not in ontology:
        raise AuditFailure('term id not in ontology', term_id, level='WARNING')

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_culture_date(value, system):
    if value['status'] == 'deleted':
        return

    if ('culture_start_date' not in value) or ('culture_harvest_date' not in value):
        return

    if value['culture_harvest_date'] <= value['culture_start_date']:
        detail = 'culture_harvest_date precedes culture_start_date'
        raise AuditFailure('invalid dates', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_donor(value, system):
    if value['status'] == 'deleted':
        return

    if ('donor' not in value) and (not value['pooled_from']):
        detail = 'biosample donor is missing'
        raise AuditFailure('missing donor', detail, level='ERROR')
        return

    if ('donor' not in value) and (value['pooled_from']):
        return

    donor = value['donor']
    if value['organism']['name'] != donor['organism']['name']:
        detail = 'biosample and donor organism mismatch'
        raise AuditFailure('organism mismatch', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_subcellular_term_match(value, system):
    if value['status'] == 'deleted':
        return

    if ('subcellular_fraction_term_name' not in value) or ('subcellular_fraction_term_id' not in value):
        return

    if (term_mapping[value['subcellular_fraction_term_name']]) != (value['subcellular_fraction_term_id']):
        detail = '{} - {}'.format(value['subcellular_fraction_term_name'], value['subcellular_fraction_term_id'])
        raise AuditFailure('subcellular term mismatch', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_depleted_term_match(value, system):
    if value['status'] == 'deleted':
        return

    if 'depleted_in_term_name' not in value:
        return

    if len(value['depleted_in_term_name']) != len(value['depleted_in_term_id']):
        detail = 'depleted_in_term_name and depleted_in_term_id totals do not match'
        raise AuditFailure('depleted_in length mismatch', detail, level='ERROR')
        return

    for i, dep_term in enumerate(value['depleted_in_term_name']):
        if (term_mapping[dep_term]) != (value['depleted_in_term_id'][i]):
            detail = '{} - {}'.format(dep_term, value['depleted_in_term_id'][i])
            raise AuditFailure('depleted_in term mismatch', detail, level='ERROR')


@audit_checker('biosample')
def audit_biosample_transfection_type(value, system):
    if value['status'] == 'deleted':
        return

    if (value['rnais']) and ('transfection_type' not in value):
        detail = 'transfection_type is missing'
        raise AuditFailure('missing transfection_type', detail, level='ERROR')

    if (value['constructs']) and ('transfection_type' not in value):
        detail = 'transfection_type is missing'
        raise AuditFailure('missing transfection_type', detail, level='ERROR')
