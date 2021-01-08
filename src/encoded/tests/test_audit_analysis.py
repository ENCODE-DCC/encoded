import pytest


def test_audit_dnase_footprints(
    testapp,
    base_analysis,
    GRCh38_file,
    replicate_dnase,
    analysis_step_run_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    encode4_award,
    dnase_footprinting_quality_metric,
):
    testapp.patch_json(
        base_analysis['@id'], {'files': [GRCh38_file['@id']]}
    )
    testapp.patch_json(
        GRCh38_file['@id'],
        {
            'replicate': replicate_dnase['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': encode4_award['@id'],
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing footprints'
        for error in res.json['audit']['WARNING']
    )
    assert all(
        error['category'] != 'no significant footprints'
        for errors in res.json['audit'].values()
        for error in errors
    )

    testapp.patch_json(
        GRCh38_file['@id'], {'output_type': 'footprints'}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].values()
        for error in errors
    )
    assert all(
        error['category'] != 'no significant footprints'
        for errors in res.json['audit'].values()
        for error in errors
    )

    testapp.patch_json(
        dnase_footprinting_quality_metric['@id'], {'footprint_count': 0}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(
        error['category'] == 'no significant footprints'
        for error in res.json['audit']['WARNING']
    )
