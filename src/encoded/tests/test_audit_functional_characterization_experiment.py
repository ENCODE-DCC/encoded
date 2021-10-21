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


def test_audit_experiment_biosample(
    testapp,
    base_fcc_experiment,
    base_replicate,
    library_url,
    biosample,
    heart,
    ntr_biosample_type
):
    testapp.patch_json(
        base_replicate['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_url['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'NTR biosample'
        for error in collect_audit_errors(res)
    )
    assert all(
        error['category'] != 'missing biosample'
        for error in collect_audit_errors(res)
    )
    assert all(
        error['category'] != 'inconsistent library biosample'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        base_fcc_experiment['@id'],
        {'biosample_ontology': ntr_biosample_type['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'NTR biosample'
        for error in collect_audit_errors(res)
    )
    assert any(
        error['category'] == 'inconsistent library biosample'
        for error in collect_audit_errors(res)
    )
    lib_edit = testapp.get(library_url['@id'] + '?frame=edit').json
    lib_edit.pop('biosample')
    testapp.put_json(library_url['@id'], lib_edit)
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing biosample'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_documents(
    testapp, base_fcc_experiment, base_replicate, library_url
):
    testapp.patch_json(
        base_replicate['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_url['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing documents'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_missing_modification(
    testapp,
    base_fcc_experiment,
    base_replicate,
    library_url,
    biosample,
    interference_genetic_modification
):
    testapp.patch_json(
        base_replicate['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_url['@id']}
    )
    testapp.patch_json(library_url['@id'], {'biosample': biosample['@id']})
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing genetic modification'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        biosample['@id'],
        {'genetic_modifications': [interference_genetic_modification['@id']]}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing genetic modification'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_released_with_unreleased_files(
    testapp, base_fcc_experiment, file_fastq
):
    testapp.patch_json(
        base_fcc_experiment['@id'],
        {'status': 'released', 'date_released': '2016-01-01'}
    )
    testapp.patch_json(
        file_fastq['@id'],
        {'dataset': base_fcc_experiment['@id'], 'status': 'in progress'}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'mismatched file status'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_replicate_with_archived_file(
    testapp, file_fastq, base_fcc_experiment, base_replicate
):
    testapp.patch_json(
        file_fastq['@id'],
        {
            'dataset': base_fcc_experiment['@id'],
            'replicate': base_replicate['@id'],
            'status': 'archived',
        }
    )
    testapp.patch_json(
        base_replicate['@id'], {'experiment': base_fcc_experiment['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert all(
        (error['category'] != 'missing raw data in replicate')
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_replicate_with_no_fastq_files(
    testapp, file_bam, base_fcc_experiment, base_replicate,
):
    testapp.patch_json(
        file_bam['@id'],
        {
            'dataset': base_fcc_experiment['@id'],
            'replicate': base_replicate['@id'],
        }
    )
    testapp.patch_json(
        base_replicate['@id'], {'experiment': base_fcc_experiment['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing raw data in replicate'
        for error in collect_audit_errors(res, ['ERROR'])
    )


def test_audit_experiment_replicated(
    testapp, base_fcc_experiment, base_replicate, pooled_clone_sequencing
):
    testapp.patch_json(
        base_fcc_experiment['@id'],
        {'status': 'submitted', 'date_submitted': '2015-03-03'}
    )
    testapp.patch_json(
        base_replicate['@id'], {'experiment': base_fcc_experiment['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'unreplicated experiment'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        base_replicate['@id'], {'experiment': pooled_clone_sequencing['@id']}
    )
    testapp.patch_json(
        pooled_clone_sequencing['@id'],
        {'status': 'submitted', 'date_submitted': '2015-03-03'}
    )
    res = testapp.get(pooled_clone_sequencing['@id'] + '@@index-data')
    assert all(
        error['category'] != 'unreplicated experiment'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_biological_replicates_biosample(
    testapp,
    base_fcc_experiment,
    base_biosample,
    library_1,
    library_2,
    replicate_1_1,
    replicate_2_1
):
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(
        replicate_1_1['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_1['@id']}
    )
    testapp.patch_json(
        replicate_2_1['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_2['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'biological replicates with identical biosample'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_technical_replicates_biosample(
    testapp,
    base_fcc_experiment,
    biosample_1,
    biosample_2,
    library_1,
    library_2,
    replicate_1_1,
    replicate_1_2
):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(
        replicate_1_1['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_1['@id']}
    )
    testapp.patch_json(
        replicate_1_2['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_2['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'technical replicates with not identical biosample'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_technical_replicates_same_library(
    testapp,
    base_fcc_experiment,
    replicate_1_1,
    replicate_1_2,
    library_1
):
    testapp.patch_json(
        replicate_1_1['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_1['@id']}
    )
    testapp.patch_json(
        replicate_1_2['@id'],
        {'experiment': base_fcc_experiment['@id'], 'library': library_1['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'sequencing runs labeled as technical replicates'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_with_libraryless_replicated(
    testapp, base_fcc_experiment, base_replicate
):
    testapp.patch_json(
        base_replicate['@id'], {'experiment': base_fcc_experiment['@id']}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'replicate with no library'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_uploading_files(
    testapp, file, base_fcc_experiment
):
    testapp.patch_json(
        file['@id'],
        {'dataset': base_fcc_experiment['@id'], 'status': 'upload failed'}
    )
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'file validation error'
        for error in collect_audit_errors(res)
    )
    assert all(
        error['category'] != 'file in uploading state'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(file['@id'], {'status': 'uploading'})
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'file in uploading state'
        for error in collect_audit_errors(res)
    )
    assert all(
        error['category'] != 'file validation error'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_inconsistent_genetic_modifications(
        testapp,
        construct_genetic_modification,
        interference_genetic_modification,
        genetic_modification,
        base_fcc_experiment,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2):
    # one biosample with genetic modifications and one biosample without genetic modifications
    testapp.patch_json(biosample_1['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'experiment': base_fcc_experiment['@id'], 'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'experiment': base_fcc_experiment['@id'], 'library': library_2['@id']})
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))
    # biosamples with the same genetic modifications
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))
    # biosamples with different genetic modifications
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [interference_genetic_modification['@id']]})
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))
    # biosamples with two genetic modifications each, with one different genetic modification for each biosample
    testapp.patch_json(biosample_1['@id'],
                       {'genetic_modifications': [interference_genetic_modification['@id'], genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id'], genetic_modification['@id']]})
    res = testapp.get(base_fcc_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))


def test_audit_experiment_mixed_expression_measurement_methods(
        testapp, file, functional_characterization_experiment_disruption_screen, ctcf):
    # https://encodedcc.atlassian.net/browse/ENCD-5903
    testapp.patch_json(
        functional_characterization_experiment_disruption_screen['@id'],
        {'examined_loci': [
            {'gene': ctcf['uuid'], 'expression_percentile': 100, 'expression_measurement_method': 'HCR-FlowFISH'},
            {'gene': ctcf['uuid'], 'expression_percentile': 10, 'expression_measurement_method': 'PrimeFlow'}
        ]})
    res = testapp.get(functional_characterization_experiment_disruption_screen['@id'] + '@@index-data')
    assert any(
        error['category'] == 'mixed expression_measurement_method'
        for error in collect_audit_errors(res)
    )


def test_audit_CRISPR_not_in_series(
    testapp,
    functional_characterization_experiment_disruption_screen,
    base_functional_characterization_series
):
    # https://encodedcc.atlassian.net/browse/ENCD-6048
    res = testapp.get(
        functional_characterization_experiment_disruption_screen['@id'] + '@@index-data')
    assert any(error['category'] == 'missing related_series'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_functional_characterization_series['@id'], {
        'related_datasets': [
            functional_characterization_experiment_disruption_screen['@id']]})
    res = testapp.get(
        functional_characterization_experiment_disruption_screen['@id'] + '@@index-data')
    assert all(error['category'] != 'missing related_series'
               for error in collect_audit_errors(res))
