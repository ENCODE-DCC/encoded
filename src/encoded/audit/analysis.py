from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_dnase_footprints(value, system):
    if 'ENCODE4' not in value['pipeline_award_rfas']:
        return
    if all(
        pipeline['title'] != 'DNase-seq pipeline'
        for pipeline in value['pipelines']
    ):
        return

    has_footprints = False
    zero_footprints_reps = set()
    for f in value['files']:
        if f['output_type'] != 'footprints':
            continue
        has_footprints = True
        for qm in f['quality_metrics']:
            if 'footprint_count' in qm and qm['footprint_count'] == 0:
                zero_footprints_reps |= set(f['technical_replicates'])

    if not has_footprints:
        detail = (
            'Missing footprints in ENCODE4 DNase-seq '
            f'analysis {audit_link(path_to_text(value["@id"]), value["@id"])}'
        )
        yield AuditFailure('missing footprints', detail, level='ERROR')
        return

    # Assume at least one qm['footprint_count'] exists?
    for rep in zero_footprints_reps:
        detail = f'Replicate {rep} has no significant footprints detected.'
        yield AuditFailure(
            'missing footprints', detail, level='WARNING'
        )


function_dispatcher = {
    'audit_dnase_footprints': audit_dnase_footprints,
}


@audit_checker(
    'Analysis',
    frame=[
        'files',
        'files.quality_metrics',
        'pipelines',
    ])
def audit_analysis(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
