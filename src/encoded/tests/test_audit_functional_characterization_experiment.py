import pytest, re
from .test_audit_experiment import (
    collect_audit_errors
)


def test_audit_experiment_lacking_processed_data(
    testapp,
    base_fcc_experiment,
    experiment,
    file_fastq,
    file_bam
    ):

    testapp.patch_json(file_fastq['@id'], {
        'dataset': base_fcc_experiment['@id'],
        })
    testapp.patch_json(file_bam['@id'], {
        'dataset': base_fcc_experiment['@id'],
        })
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(warning['category'] != 'lacking processed data'
        for warning in collect_audit_errors(res))
    testapp.patch_json(file_bam['@id'], {
        'dataset': experiment['@id']
        })
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(warning['category'] == 'lacking processed data'
        for warning in collect_audit_errors(res))