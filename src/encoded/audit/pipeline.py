from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
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
    diff_links = [audit_link(path_to_text(d), d) for d in diff]
    if diff:
        detail = ', '.join(sorted(diff_links))
        yield AuditFailure('incomplete analysis_steps', detail, level='ERROR')


# def audit_pipeline_assay(value, system):
# https://encodedcc.atlassian.net/browse/ENCD-3416
