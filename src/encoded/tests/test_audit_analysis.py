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
        for error in res.json['audit'].get('ERROR', [])
    )
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('WARNING', [])
        for error in errors
    )

    testapp.patch_json(
        GRCh38_file['@id'], {'output_type': 'footprints'}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('ERROR', [])
        for error in errors
    )
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('WARNING', [])
        for error in errors
    )

    testapp.patch_json(
        dnase_footprinting_quality_metric['@id'], {'footprint_count': 0}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('ERROR', [])
        for error in errors
    )
    assert any(
        error['category'] == 'missing footprints'
        for error in res.json['audit'].get('WARNING', [])
    )


def test_audit_dnase_encode3(
    testapp,
    base_analysis,
    base_experiment,
    file_tsv_1_1,
    file_bam_1_1,
    bigWig_file,
    correlation_quality_metric,
    hotspot_quality_metric,
    chip_seq_quality_metric,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_dnase_encode4,
    analysis_step_version_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    encode4_award,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [bigWig_file['@id']],
        'Pearson correlation': 0.15})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(
        bigWig_file['@id'],
        {
            'output_type': 'read-depth normalized signal',
            'dataset': base_experiment['@id'],
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'hotspots',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_1['@id'],
            file_bam_1_1['@id'],
            bigWig_file['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'DNase-HS pipeline single-end - Version 2',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low spot score' for error in res.json['audit'].get('WARNING', []))
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in res.json['audit'].get('NOT_COMPLIANT', []))


def test_audit_dnase_encode4(
    testapp,
    base_analysis,
    base_experiment,
    file_tsv_1_1,
    file_bam_1_1,
    bigWig_file,
    correlation_quality_metric,
    hotspot_quality_metric,
    chip_seq_quality_metric,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_dnase_encode4,
    analysis_step_version_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    encode4_award,
    encode_lab
):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [bigWig_file['@id']],
        'Pearson correlation': 0.15})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(
        bigWig_file['@id'],
        {
            'output_type': 'read-depth normalized signal',
            'dataset': base_experiment['@id'],
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'hotspots',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_1['@id'],
            file_bam_1_1['@id'],
            bigWig_file['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': encode4_award['@id'],
            'title': 'DNase-seq pipeline',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low spot score' for error in res.json['audit'].get('WARNING', []))
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))


def test_audit_dnase_missing_read_depth(
    testapp,
    base_analysis,
    base_experiment,
    file_tsv_1_1,
    file_bam_1_1,
    chip_seq_quality_metric,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_dnase_encode4,
    analysis_step_version_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(chip_seq_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_1['@id']]})
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bam_1_1['@id'],
        ]}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'DNase-HS pipeline single-end - Version 2',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing read depth' for error in res.json['audit'].get('INTERNAL_ACTION', []))
