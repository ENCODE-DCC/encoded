from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker(
    'Analysis',
    frame=['analysis_step_runs.analysis_step_version.analysis_step']
)
def audit_mismatch_pipeline(value, system):
    '''
    Analysis pipeline needs to match pipelines its step runs belong to.
    '''
    if 'pipeline' not in value:
        return
    analysis_pipeline = value['pipeline']
    for step_run in value['analysis_step_runs']:
        step = step_run['analysis_step_version']['analysis_step']
        if analysis_pipeline not in step['pipelines']:
            detail = (
                "The analysis_step_run {} belongs to {} pipelines, "
                "none of which matches analsis pipeline {}."
            ).format(
                step_run['@id'],
                ', '.join(step['pipelines']),
                analysis_pipeline
            )
            yield AuditFailure(
                'mismatch pipeline',
                detail,
                level='INTERNAL_ACTION'
            )
