from snovault import (
    AuditFailure,
    audit_checker,
)


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


# def audit_pipeline_assay(value, system):
# https://encodedcc.atlassian.net/browse/ENCD-3416
