from snovault import (
    AuditFailure,
    audit_checker,
)
from .ontology_data import NTR_assay_lookup


@audit_checker('Pipeline', frame=['analysis_steps'])
def audit_analysis_steps_closure(value, system):
    ''' The analysis_steps list should include all of a steps ancestors.
    '''
    if 'analysis_steps' not in value:
        return
    ids = {step['@id'] for step in value['analysis_steps']}
    parents = {parent for step in value['analysis_steps'] for parent in step.get('parents', [])}
    diff = parents.difference(ids)
    if diff:
        detail = ', '.join(sorted(diff))
        raise AuditFailure('incomplete analysis_steps', detail, level='ERROR')


@audit_checker('Pipeline', frame='object')
def audit_pipeline_assay(value, system):
    '''
    Pipelines should have assays with valid ontologies term ids and names that
    are a valid synonym.
    '''
    if value['status'] == 'deleted':
        return

    # Term name is required and term id is calculated, so we probably don't need this
    # audit anymore.
    if 'assay_term_id' not in value:
        detail = 'Pipeline {} is missing assay_term_id'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return
    if 'assay_term_name' not in value:
        detail = 'Pipeline {} is missing assay_term_name'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return

    ontology = system['registry']['ontology']
    term_id = value.get('assay_term_id')
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = 'assay_term_id is a New Term Request ({} - {})'.format(term_id, term_name)
        yield AuditFailure('NTR assay', detail, level='INTERNAL_ACTION')

        if term_name != NTR_assay_lookup[term_id]:
            detail = 'Pipeline has a mismatch between assay_term_name ' + \
                     '"{}" and assay_term_id "{}"'.format(term_name,
                                                          term_id)
            yield AuditFailure('inconsistent assay_term_name', detail, level='INTERNAL_ACTION')
            return
    elif term_id not in ontology:
        detail = 'Assay_term_id {} is not found in cached version of ontology'.format(term_id)
        yield AuditFailure('assay_term_id not in ontology', term_id, level='INTERNAL_ACTION')
        return

    ontology_term_name = ontology[term_id]['name']
    modifed_term_name = term_name + ' assay'
    if (ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']) and \
        (ontology_term_name != modifed_term_name and
            modifed_term_name not in ontology[term_id]['synonyms']):
        detail = 'Pipeline has a mismatch between ' + \
                 'assay_term_name "{}" and assay_term_id "{}"'.format(term_name,
                                                                      term_id)
        yield AuditFailure('inconsistent assay_term_name', detail, level='INTERNAL_ACTION')
        return
