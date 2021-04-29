import pytest


def test_assembly_from_related_datasets(testapp, base_reference_epigenome, base_experiment_submitted, hg19_file, GRCh38_file):
    # If only original file is present in series, assembly should be ['hg19']
    res = testapp.get(base_reference_epigenome['@id'] + '@@index-data')
    assert res.json['object']['assembly'] == ['hg19']
    # Adding a related_dataset with a file in GRCh38 should now give it both ['hg19', 'GRCh38']
    testapp.patch_json(base_reference_epigenome['@id'], {'related_datasets': [base_experiment_submitted['@id']]})
    res = testapp.get(base_reference_epigenome['@id'] + '@@index-data')
    assert res.json['object']['assembly'].sort() == ['hg19', 'GRCh38'].sort()
    # Setting the experiment in related_dataset to delete it should exclude its assembly from the calculation
    testapp.patch_json(base_experiment_submitted['@id'], {'status': 'deleted'})
    res = testapp.get(base_reference_epigenome['@id'] + '@@index-data')
    assert res.json['object']['assembly'] == ['hg19']


def test_assay_single_cell_rna_series(testapp, base_single_cell_series):
    res = testapp.get(base_single_cell_series['@id'] + '@@index-data')
    assert sorted(res.json['object']['assay_term_name']) == ["RNA-seq"]


def test_gene_silencing_series(testapp, base_gene_silencing_series):
    res = testapp.get(base_gene_silencing_series['@id'] + '@@index-data')
    assert sorted(res.json['object']['assay_term_name']) == ["RNA-seq"]


def test_assay_differentiation_series(testapp, base_differentiation_series):
    res = testapp.get(base_differentiation_series['@id'] + '@@index-data')
    assert sorted(res.json['object']['assay_term_name']) == ['RNA-seq']


def test_assay_pulse_chase_time_series(testapp, base_pulse_chase_time_series):
    res = testapp.get(base_pulse_chase_time_series['@id'] + '@@index-data')
    assert sorted(res.json['object']['assay_term_name']) == ['RNA-seq']


def test_assay_type_single_cell_rna_series(testapp, single_cell_series):
    res = testapp.get(single_cell_series['@id'] + '@@index-data')
    assert sorted(res.json['object']['assay_slims']) == ['Single cell']
