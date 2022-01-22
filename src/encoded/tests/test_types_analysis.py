import pytest


def test_types_analysis_title(
    testapp,
    analysis_released,
    encode4_award,
    ENCODE3_award,
    encode_lab,
    file_bam_1_1,
    file_bam_2_1,
    analysis_step_run_chip_encode4,
    analysis_step_run_dnase_encode4,
    pipeline_dnase_encode4,
    pipeline_chip_encode4,
): 
    testapp.patch_json(analysis_released['@id'], {'files': [file_bam_1_1['@id']]})
    res = testapp.get(analysis_released['@id'] + '@@index-data')
    assert res.json['object']['title'] == 'Lab custom mm10'
    
    testapp.patch_json(
        file_bam_1_1['@id'],
        {'step_run': analysis_step_run_chip_encode4['@id']}
    )
    testapp.patch_json(
        pipeline_chip_encode4['@id'], {'lab': encode_lab['@id'], 'award': encode4_award['@id']})
    res = testapp.get(analysis_released['@id'] + '@@index-data')
    assert res.json['object']['title'] == 'ENCODE4 mm10'
    
    testapp.patch_json(analysis_released['@id'], {'files': [file_bam_1_1['@id'], file_bam_2_1['@id']]})
    testapp.patch_json(
        file_bam_1_1['@id'],
        {'step_run': analysis_step_run_chip_encode4['@id']}
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {'step_run': analysis_step_run_dnase_encode4['@id']}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'], {'lab': encode_lab['@id'], 'award': ENCODE3_award['@id']}
    )
    res = testapp.get(analysis_released['@id'] + '@@index-data')
    print (res.json['object'])
    assert res.json['object']['title'] == 'Mixed uniform (ENCODE3, ENCODE4) mm10'

def test_types_analysis_quality_metrics(
    testapp,
    analysis_released,
    chip_align_enrich_quality_metric,
    file_bam_1_chip,
):
    testapp.patch_json(file_bam_1_chip['@id'], {'aliases': ["encode:file_123"]})
    testapp.patch_json(chip_align_enrich_quality_metric['@id'], {'quality_metric_of': [file_bam_1_chip['@id']]})
    testapp.patch_json(analysis_released['@id'], {'files': [file_bam_1_chip['@id']]})
    res = testapp.get(analysis_released['@id'] + '@@index-data')
    quality_metric = res.json['object']['quality_metrics'][0]
    file_res = testapp.get(file_bam_1_chip['@id'] + '@@index-data')
    file_obj = file_res.json['object']
    assert quality_metric['files'][0] == file_obj['@id']
    assert quality_metric['biological_replicates'] == [1]
    assert quality_metric['quality_metric']['NSC'] == -2.492904