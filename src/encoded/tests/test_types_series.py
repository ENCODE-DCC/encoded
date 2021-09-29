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
    assay_slims = testapp.get(single_cell_series['@id'] + '@@index-data').json['object']['assay_slims']
    assert len(assay_slims) == 2
    assert 'Single cell' in assay_slims
    assert 'Transcription' in assay_slims


def test_biosample_summary_from_related_datasets(testapp,
    treated_differentiation_series,
    experiment_1,
    experiment_2,
    donor_1,
    donor_2,
    biosample_1,
    biosample_2,
    library_1,
    library_2,
    treatment_12,
    treatment_with_duration_amount_units,
    replicate_1_1,
    replicate_2_1,
    heart,
    liver
):
    testapp.patch_json(
        biosample_1['@id'],
        {
            'donor': donor_1['@id'],
            'treatments': [treatment_12['@id']],
            'biosample_ontology': heart['uuid']
        }
    )
    testapp.patch_json(
        biosample_2['@id'],
        {
            'donor': donor_2['@id'],
            'biosample_ontology': liver['uuid'],
            'treatments': [treatment_with_duration_amount_units['@id']]
        }
    )
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(
        replicate_1_1['@id'],
        {'library': library_1['@id'], 'experiment': experiment_1['@id']}
    )
    testapp.patch_json(experiment_1['@id'], {'biosample_ontology': heart['uuid']})
    testapp.patch_json(
        replicate_2_1['@id'],
        {'library': library_2['@id'], 'experiment': experiment_2['@id']}
    )
    testapp.patch_json(experiment_2['@id'], {'biosample_ontology': liver['uuid']})
    res = testapp.get(treated_differentiation_series['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == 'Homo sapiens heart tissue treated with estradiol'

    testapp.patch_json(
        treated_differentiation_series['@id'],
        {'related_datasets': [experiment_1['@id'], experiment_2['@id']]}
    )
    res = testapp.get(treated_differentiation_series['@id']+'@@index-data')
    biosample_summary = testapp.get(treated_differentiation_series['@id']+'@@index-data').json['object']['biosample_summary']
    assert 'heart tissue' and 'liver tissue' and 'treated with' and 'ethanol' and 'estradiol' in biosample_summary

    testapp.patch_json(
        biosample_2['@id'],
        {
            'biosample_ontology': heart['uuid'],
        }
    )
    testapp.patch_json(experiment_2['@id'], {'biosample_ontology': heart['uuid']})
    res = testapp.get(treated_differentiation_series['@id']+'@@index-data')
    biosample_summary = testapp.get(treated_differentiation_series['@id']+'@@index-data').json['object']['biosample_summary']
    assert 'heart tissue treated with' and 'ethanol' and 'estradiol' in biosample_summary


def test_assay_collection_series(testapp, base_collection_series):
    res = testapp.get(base_collection_series['@id'] + '@@index-data')
    assert sorted(res.json['object']['assay_term_name']) == ['MPRA']
