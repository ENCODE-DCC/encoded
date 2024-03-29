import pytest, re
from .constants import RED_DOT

def collect_audit_errors(result, error_types=None):
    errors = result.json['audit']
    errors_list = []
    if error_types:
        for error_type in error_types:
            errors_list.extend(errors[error_type])
    else:
        for error_type in errors:
            errors_list.extend(errors[error_type])
    return errors_list


def test_audit_experiment_missing_fragmentation_method(testapp,
                                                       base_experiment,
                                                       replicate_1_1,
                                                       replicate_2_1,
                                                       library_1,
                                                       library_2):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'HiC'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing fragmentation method'
               for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_fragmentation_method(testapp,
                                                            base_experiment,
                                                            replicate_1_1,
                                                            replicate_2_1,
                                                            library_1,
                                                            library_2):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'HiC'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(library_1['@id'], {'fragmentation_methods': ['chemical (HindIII restriction)']})
    testapp.patch_json(library_2['@id'], {'fragmentation_methods': ['chemical (MboI restriction)']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent fragmentation method'
               for error in collect_audit_errors(res))


def test_audit_experiment_consistent_fragmentation_method(testapp,
                                                          base_experiment,
                                                          replicate_1_1,
                                                          replicate_2_1,
                                                          library_1,
                                                          library_2):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'HiC'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(library_1['@id'], {'fragmentation_methods': ['chemical (HindIII restriction)', 'chemical (MboI restriction)']})
    testapp.patch_json(library_2['@id'], {'fragmentation_methods': ['chemical (MboI restriction)', 'chemical (HindIII restriction)']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'inconsistent fragmentation method'
               for error in collect_audit_errors(res))


def test_audit_experiment_mixed_libraries(testapp,
                                          base_experiment,
                                          replicate_1_1,
                                          replicate_2_1,
                                          library_1,
                                          library_2):
    testapp.patch_json(library_1['@id'], {'nucleic_acid_term_name': 'DNA'})
    testapp.patch_json(library_2['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed libraries'
               for error in collect_audit_errors(res))


def test_audit_experiment_RNA_library_RIN(testapp,
                                          base_experiment,
                                          replicate_1_1,
                                          library_1):
    testapp.patch_json(library_1['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing RIN'
               for error in collect_audit_errors(res))
    testapp.patch_json(library_1['@id'], {'rna_integrity_number': 7})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RIN'
               for error in collect_audit_errors(res))


def test_audit_experiment_RNA_library_RIN_excluded_assays(testapp,
                                          base_experiment,
                                          replicate_1_1,
                                          library_1):
    testapp.patch_json(library_1['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'],{'assay_term_name': 'eCLIP'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] != 'missing RIN'
               for error in collect_audit_errors(res))


def test_audit_experiment_released_with_unreleased_files(testapp, base_experiment, file_fastq):
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    testapp.patch_json(file_fastq['@id'], {'status': 'in progress'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mismatched file status'
               for error in collect_audit_errors(res))


def test_ChIP_possible_control(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep):
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'invalid possible_control'
               for error in collect_audit_errors(res))


def test_ChIP_possible_control_roadmap(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep,
                                       award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'invalid possible_control'
               for error in collect_audit_errors(res))


def test_audit_input_control(
    testapp,
    base_experiment,
    ctrl_experiment,
    construct_genetic_modification,
    base_biosample,
    base_library,
    base_replicate,
):
    # Non-tagged ChIP
    testapp.patch_json(
        base_experiment['@id'],
        {
            'possible_controls': [ctrl_experiment['@id']],
            'assay_term_name': 'ChIP-seq'
        }
    )
    testapp.patch_json(ctrl_experiment['@id'], {'control_type': 'wild type'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing input control'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        ctrl_experiment['@id'], {'control_type': 'input library'}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing input control'
        for error in collect_audit_errors(res)
    )

    # Non-tagged Mint-ChIP
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'Mint-ChIP-seq'})
    testapp.patch_json(ctrl_experiment['@id'], {'control_type': 'wild type'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing input control'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(ctrl_experiment['@id'], {'control_type': 'input library'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing input control'
        for error in collect_audit_errors(res)
    )

    # Tagged ChIP
    testapp.patch_json(
        construct_genetic_modification['@id'],
        {'introduced_tags': [{'name': 'FLAG', 'location': 'internal'}]}
    )
    testapp.patch_json(
        base_biosample['@id'],
        {'genetic_modifications': [construct_genetic_modification['@id']]}
    )
    testapp.patch_json(
        base_replicate['@id'], {'library': base_library['@id']}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing input control'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        ctrl_experiment['@id'], {'control_type': 'control'}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing input control'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        ctrl_experiment['@id'], {'control_type': 'wild type'}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing input control'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_target(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing target'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'PLAC-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing target'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'CUT&RUN'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing target'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'CUT&Tag'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing target'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicated(testapp, base_experiment, base_replicate, base_library, a549):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'unreplicated experiment' and error['level_name'] == 'INTERNAL_ACTION'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'biosample_ontology': a549['uuid']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'unreplicated experiment' and error['level_name'] == 'NOT_COMPLIANT'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'single-cell RNA sequencing assay'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read single-cell RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'replicates': []})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'unreplicated experiment' and error['level_name'] == 'NOT_COMPLIANT'
                for error in collect_audit_errors(res))


def test_audit_experiment_technical_replicates_same_library(testapp, base_experiment,
                                                            base_replicate, base_replicate_two,
                                                            base_library):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_replicate_two['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {
                       'replicates': [base_replicate['@id'], base_replicate_two['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'sequencing runs labeled as technical replicates'
               for error in collect_audit_errors(res))


def test_audit_experiment_biological_replicates_biosample(
        testapp, base_experiment, base_biosample,
        library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'biological replicates with identical biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_technical_replicates_biosample(
        testapp, base_experiment, biosample_1, biosample_2,
        library_1, library_2, replicate_1_1, replicate_1_2):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'technical replicates with not identical biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_libraryless_replicated(
        testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    testapp.patch_json(base_experiment['@id'], {'replicates': [base_replicate['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'replicate with no library'
               for error in collect_audit_errors(res))


def test_audit_experiment_single_cell_replicated(
        testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'single-cell RNA sequencing assay'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_RNA_bind_n_seq_replicated(testapp, base_experiment, base_replicate,
                                                    base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'RNA Bind-n-Seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_roadmap_replicated(
        testapp, base_experiment, base_replicate, base_library, award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'award': award['@id']})
    testapp.patch_json(base_experiment['@id'],
                       {'status': 'released', 'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_spikeins(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_library['@id'], {'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing spikeins'
               for error in collect_audit_errors(res))


def test_audit_experiment_target_mismatch(
        testapp, base_experiment, base_replicate, base_target, antibody_lot):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(
        base_experiment['@id'], {'assay_term_name': 'ChIP-seq', 'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent target'
               for error in collect_audit_errors(res))


def test_audit_experiment_no_characterizations_antibody(testapp,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library,
                                                        base_biosample,
                                                        antibody_lot,
                                                        target,
                                                        k562):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'],
                                               'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': k562['uuid'],
                                                'target': target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'uncharacterized antibody'
               for error in collect_audit_errors(res))


def test_audit_experiment_wrong_organism_histone_antibody(testapp,
                                                          base_experiment,
                                                          wrangler,
                                                          base_antibody,
                                                          base_replicate,
                                                          base_library,
                                                          base_biosample,
                                                          mouse_H3K9me3,
                                                          target_H3K9me3,
                                                          base_antibody_characterization1,
                                                          base_antibody_characterization2,
                                                          mouse,
                                                          human,
                                                          k562,
                                                          mel):
    # Mouse biosample in mouse ChIP-seq experiment but supporting antibody characterizations
    # are compliant in human but not mouse.
    base_antibody['targets'] = [mouse_H3K9me3['@id'], target_H3K9me3['@id']]
    histone_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_biosample['@id'], {'organism': mouse['@id']})
    characterization_reviews = [
        {
            'biosample_ontology': mel['uuid'],
            'organism': mouse['@id'],
            'lane_status': 'not compliant',
            'lane': 1
        },
        {
            'biosample_ontology': k562['uuid'],
            'organism': human['@id'],
            'lane_status': 'compliant',
            'lane': 2
        }
    ]
    testapp.patch_json(
        base_antibody_characterization1['@id'],
        {'target': target_H3K9me3['@id'],
            'characterizes': histone_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'characterization_reviews': characterization_reviews})
    testapp.patch_json(
        base_antibody_characterization2['@id'],
        {'target': target_H3K9me3['@id'],
            'characterizes': histone_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id']})
    testapp.patch_json(base_replicate['@id'], {'antibody': histone_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': mel['uuid'],
                                                'target': mouse_H3K9me3['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'antibody not characterized to standard'
               for error in collect_audit_errors(res))


def test_audit_experiment_partially_characterized_antibody(testapp,
                                                           base_experiment,
                                                           wrangler,
                                                           base_target,
                                                           base_antibody,
                                                           base_replicate,
                                                           base_library,
                                                           base_biosample,
                                                           base_antibody_characterization1,
                                                           base_antibody_characterization2,
                                                           human,
                                                           hepg2,
                                                           k562):
    # K562 biosample in ChIP-seq experiment with exempt primary in K562 and in progress
    # secondary - leading to partial characterization.
    base_antibody['targets'] = [base_target['@id']]
    TF_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    characterization_reviews = [
        {
            'biosample_ontology': hepg2['uuid'],
            'organism': human['@id'],
            'lane_status': 'not compliant',
            'lane': 1
        },
        {
            'biosample_ontology': k562['uuid'],
            'organism': human['@id'],
            'lane_status': 'exempt from standards',
            'lane': 2
        }
    ]
    testapp.patch_json(
        base_antibody_characterization1['@id'],
        {'target': base_target['@id'],
            'characterizes': TF_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'characterization_reviews': characterization_reviews})

    testapp.patch_json(base_replicate['@id'], {'antibody': TF_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': k562['uuid'],
                                                'target': base_target['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'partially characterized antibody'
               for error in collect_audit_errors(res))


def test_audit_experiment_antibody_characterizations_NTR_biosample(testapp,
                                                           base_experiment,
                                                           wrangler,
                                                           base_target,
                                                           base_antibody,
                                                           base_replicate,
                                                           base_library,
                                                           base_antibody_characterization1,
                                                           human,
                                                           hepg2,
                                                           ntr_biosample_type):
    # Antibody has characterization reviews on a NTR biosample type
    base_antibody['targets'] = [base_target['@id']]
    TF_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    characterization_reviews = [
        {
            'biosample_ontology': hepg2['uuid'],
            'organism': human['@id'],
            'lane_status': 'compliant',
            'lane': 1
        },
        {
            'biosample_ontology': ntr_biosample_type['uuid'],
            'organism': human['@id'],
            'lane_status': 'exempt from standards',
            'lane': 2
        }
    ]
    testapp.patch_json(
        base_antibody_characterization1['@id'],
        {'target': base_target['@id'],
            'characterizes': TF_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'characterization_reviews': characterization_reviews})

    testapp.patch_json(base_replicate['@id'], {'antibody': TF_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': hepg2['uuid'],
                                                'target': base_target['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert not any(error['category'] == 'NTR biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_geo_submission(testapp, base_experiment):
    testapp.patch_json(
        base_experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'experiment not submitted to GEO'
               for error in collect_audit_errors(res))


def test_audit_experiment_biosample_match(testapp, base_experiment,
                                          base_biosample, base_replicate,
                                          base_library, h1, ileum, biosample_1,
                                          biosample_2, library_no_biosample,
                                          base_replicate_two):
    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': h1['uuid']})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'biosample_ontology': ileum['uuid']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent library biosample'
               for error in collect_audit_errors(res))

    # https://encodedcc.atlassian.net/browse/ENCD-5674
    testapp.patch_json(library_no_biosample['@id'], {'mixed_biosamples': [biosample_1['@id'], biosample_2['@id']]})
    testapp.patch_json(base_replicate_two['@id'], {'library': library_no_biosample['@id']})
    res_errors = collect_audit_errors(testapp.get(base_experiment['@id'] + '@@index-data'))
    assert any(error['category'] == 'inconsistent library biosample'
               and 'generated from mixed biosamples' in error['detail']
               for error in res_errors)
    assert any(error['category'] == 'inconsistent library biosample'
               and 'both standard and mixed biosamples' in error['detail']
               for error in res_errors)


def test_audit_experiment_biosample_and_mixed_biosamples(testapp, base_experiment, base_replicate,
                                                         base_library, library_no_biosample, biosample_1,
                                                         biosample_2, base_replicate_two):
    # https://encodedcc.atlassian.net/browse/ENCD-5674
    testapp.patch_json(library_no_biosample['@id'],
                       {'mixed_biosamples': [biosample_1['@id'], biosample_2['@id']]})
    testapp.patch_json(base_replicate_two['@id'],
                       {'library': library_no_biosample['@id']})
    testapp.patch_json(base_replicate['@id'],
                       {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent library biosample'
               for error in collect_audit_errors(res))

def test_audit_experiment_documents(testapp, base_experiment, base_library, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing documents'
               for error in collect_audit_errors(res))


def test_audit_experiment_documents_excluded(testapp, base_experiment,
                                             base_library, award, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(award['@id'], {'rfa': 'modENCODE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] != 'missing documents'
               for error in collect_audit_errors(res))

def test_audit_experiment_links_included(testapp, base_experiment,
                                             base_library, award, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(award['@id'], {'rfa': 'modENCODE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(re.search(r'{.+?\|.+?}', error['detail'])
               for error in collect_audit_errors(res))


def test_audit_experiment_model_organism_mismatched_sex(testapp,
                                                        base_experiment,
                                                        replicate_1_1,
                                                        replicate_2_1,
                                                        library_1,
                                                        library_2,
                                                        biosample_1,
                                                        biosample_2,
                                                        mouse_donor_1_6):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'male'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'female'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent sex'
               for error in collect_audit_errors(res))


def test_audit_experiment_model_organism_mismatched_age(testapp,
                                                        base_experiment,
                                                        replicate_1_1,
                                                        replicate_2_1,
                                                        library_1,
                                                        library_2,
                                                        biosample_1,
                                                        biosample_2,
                                                        mouse_donor_1_6,
                                                        mouse_donor_2):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '51'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent age'
               for error in collect_audit_errors(res))


def test_audit_experiment_model_organism_mismatched_donor(testapp,
                                                          base_experiment,
                                                          replicate_1_1,
                                                          replicate_2_1,
                                                          library_1,
                                                          library_2,
                                                          biosample_1,
                                                          biosample_2,
                                                          mouse_donor_1_6,
                                                          mouse_donor_2_6):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_2_6['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent donor'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_library_without_biosample(testapp, base_experiment, base_replicate,
                                                         library_no_biosample, biosample_1,
                                                         biosample_2):
    testapp.patch_json(base_replicate['@id'], {'library': library_no_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing biosample'
               for error in collect_audit_errors(res))
    testapp.patch_json(library_no_biosample['@id'], {'mixed_biosamples': [biosample_1['@id'], biosample_2['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_no_size_range(
    testapp,
    experiment_with_RNA_library,
):
    res = testapp.get(experiment_with_RNA_library.json['object']['@id'] + '@@index-data')
    assert any(error['category'] == 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_with_size_range(
    testapp,
    experiment_with_RNA_library,
    base_library,
):
    testapp.patch_json(base_library['@id'], {'size_range': '>200'})
    res = testapp.get(experiment_with_RNA_library.json['object']['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_no_size_range_RNA_microarray(
    testapp,
    experiment_with_RNA_library,
):
    testapp.patch_json(experiment_with_RNA_library.json['object']['@id'], {'assay_term_name': 'transcription profiling by array assay'})
    res = testapp.get(experiment_with_RNA_library.json['object']['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_no_size_range_long_read_RNA(
    testapp,
    experiment_with_RNA_library,
):
    testapp.patch_json(experiment_with_RNA_library.json['object']['@id'], {'assay_term_name': 'long read RNA-seq'})
    res = testapp.get(experiment_with_RNA_library.json['object']['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_no_size_range_Bru_seq(
    testapp,
    experiment_with_RNA_library,
):
    # https://encodedcc.atlassian.net/browse/ENCD-5457
    testapp.patch_json(experiment_with_RNA_library.json['object']['@id'], {'assay_term_name': 'Bru-seq'})
    res = testapp.get(experiment_with_RNA_library.json['object']['@id'] + '@@index-data')
    assert any(error['category'] == 'missing RNA fragment size'
               for error in collect_audit_errors(res, error_types=['WARNING']))

    assert all(error['category'] != 'missing RNA fragment size'
               for error in collect_audit_errors(res, error_types=['NOT_COMPLIANT']))


def test_audit_experiment_with_RNA_library_missing_read_length_long_read_RNA_seq(
    testapp,
    experiment_no_read_length,
    pipeline_bam,
):
    testapp.patch_json(pipeline_bam['@id'], {'title': 'Long read RNA-seq pipeline'})
    res = testapp.get(experiment_no_read_length.json['object']['@id'] + '@@index-data')
    assert all(error['category'] != 'missing read_length'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_missing_read_length_RNA_seq(
    testapp,
    experiment_no_read_length,
    pipeline_bam,
):
    testapp.patch_json(pipeline_bam['@id'], {'title': 'RNA-seq of long RNAs (paired-end, stranded)'})
    res = testapp.get(experiment_no_read_length.json['object']['@id'] + '@@index-data')
    assert any(error['category'] == 'missing read_length'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_missing_read_length_bulk_RNA_seq(
    testapp,
    experiment_no_read_length,
    pipeline_bam,
):
    testapp.patch_json(pipeline_bam['@id'], {'title': 'Bulk RNA-seq'})
    res = testapp.get(experiment_no_read_length.json['object']['@id'] + '@@index-data')
    assert any(error['category'] == 'missing read_length'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_file(testapp, file_fastq,
                                              base_experiment,
                                              base_replicate,
                                              base_library):
    testapp.patch_json(file_fastq['@id'], {'replicate': base_replicate['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all((error['category'] != 'missing raw data in replicate')
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_archived_file(
        testapp,
        file_fastq,
        base_experiment,
        base_replicate,
        base_library
    ):
    testapp.patch_json(file_fastq['@id'], {
        'replicate': base_replicate['@id'],
        'status': 'archived'})
    testapp.patch_json(base_experiment['@id'], {
        'assay_term_name': 'RNA-seq',
        'status': 'released',
        'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all((error['category'] != 'missing raw data in replicate')
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_fastq_files(testapp, file_bam,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing raw data in replicate'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_files(testapp,
                                                  base_experiment,
                                                  base_replicate,
                                                  base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing raw data in replicate'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_files_dream(testapp,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq',
                                                'internal_tags': ['DREAM'],
                                                'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing raw data in replicate'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_files_warning(testapp, file_bed_methyl,
                                                          base_experiment,
                                                          base_replicate,
                                                          base_library):
    testapp.patch_json(file_bed_methyl['@id'], {'replicate': base_replicate['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'in progress'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing raw data in replicate' for
               error in collect_audit_errors(res, ['ERROR']))


def test_audit_experiment_pipeline_assay_term_name_consistency(
        testapp,
        experiment, bam_file,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam):
    testapp.patch_json(experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    testapp.patch_json(bam_file['@id'], {'step_run': analysis_step_run_bam['@id']})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (single-end, unstranded)',
                                             'assay_term_names': ['RNA-seq', 'RAMPAGE']})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent assay_term_name'
               for error in collect_audit_errors(res))


def test_audit_experiment_pipeline_without_assay_term_names(
        testapp,
        experiment, bam_file,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_without_assay_term_names_bam):
    testapp.patch_json(experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    testapp.patch_json(bam_file['@id'], {'step_run': analysis_step_run_bam['@id']})
    testapp.patch_json(pipeline_without_assay_term_names_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (single-end, unstranded)'})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent assay_term_name'
               for error in collect_audit_errors(res))


def test_audit_experiment_not_uploaded_files(testapp, file_bam,
                                             base_experiment,
                                             base_replicate,
                                             base_library):
    testapp.patch_json(file_bam['@id'], {'status': 'upload failed'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'file validation error'
               for error in collect_audit_errors(res))


def test_audit_experiment_uploading_files(testapp, file_bam,
                                          base_experiment,
                                          base_replicate,
                                          base_library):
    testapp.patch_json(file_bam['@id'], {'status': 'uploading'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'file validation error'
               for error in collect_audit_errors(res))
    assert any(error['category'] == 'file in uploading state'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_length_sequencing_files(testapp, file_bam, file_fastq,
                                                             base_experiment, file_fastq_2,
                                                             base_replicate,
                                                             base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed run types'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_platforms(testapp, file_fastq,
                                               base_experiment, file_fastq_2,
                                               base_replicate, platform1,
                                               base_library, platform2):
    testapp.patch_json(file_fastq['@id'], {'platform': platform1['@id']})
    testapp.patch_json(file_fastq_2['@id'], {'platform': platform2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent platforms'
               for error in collect_audit_errors(res))


def test_audit_experiment_archived_files_mismatched_platforms(
        testapp, file_fastq, base_experiment, file_fastq_2, base_replicate,
        platform1, base_library, platform2):
    testapp.patch_json(file_fastq['@id'], {'platform': platform1['@id'],
                                           'status': 'archived'})
    testapp.patch_json(file_fastq_2['@id'], {'platform': platform2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'inconsistent platforms'
               for error in collect_audit_errors(res))


def test_audit_experiment_internal_tag(testapp, base_experiment,
                                       base_biosample,
                                       library_1,
                                       replicate_1_1):
    testapp.patch_json(base_biosample['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent internal tags'
               for error in collect_audit_errors(res))


def test_audit_experiment_internal_tags(testapp, base_experiment,
                                        biosample_1,
                                        biosample_2,
                                        library_1,
                                        library_2,
                                        replicate_1_1,
                                        replicate_1_2):
    testapp.patch_json(biosample_1['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'internal_tags': ['ENTEx', 'SESCC']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent internal tags'
               for error in collect_audit_errors(res))


def test_audit_experiment_internal_tags2(testapp, base_experiment,
                                         biosample_1,
                                         biosample_2,
                                         library_1,
                                         library_2,
                                         replicate_1_1,
                                         replicate_1_2):
    testapp.patch_json(biosample_1['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent internal tags' for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_inter_paired_sequencing_files(testapp,
                                                                   base_experiment,
                                                                   replicate_1_1,
                                                                   replicate_2_1,
                                                                   library_1,
                                                                   library_2,
                                                                   biosample_1,
                                                                   biosample_2,
                                                                   mouse_donor_1_6,
                                                                   mouse_donor_2,
                                                                   file_fastq_6,
                                                                   file_fastq_4):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed run types'
               for error in collect_audit_errors(res))


def test_audit_experiment_DNase_mismatched_inter_paired_sequencing_files(testapp,
                                                                         base_experiment,
                                                                         replicate_1_1,
                                                                         replicate_2_1,
                                                                         library_1,
                                                                         library_2,
                                                                         biosample_1,
                                                                         biosample_2,
                                                                         mouse_donor_1_6,
                                                                         mouse_donor_2,
                                                                         file_fastq_6,
                                                                         file_fastq_4):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'mixed run types'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_inter_length_sequencing_files(testapp,
                                                                   base_experiment,
                                                                   replicate_1_1,
                                                                   replicate_2_1,
                                                                   library_1,
                                                                   library_2,
                                                                   biosample_1,
                                                                   biosample_2,
                                                                   mouse_donor_1_6,
                                                                   mouse_donor_2,
                                                                   file_fastq_3,
                                                                   file_fastq_4,
                                                                   file_fastq_5):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 50})
    testapp.patch_json(file_fastq_5['@id'], {'read_length': 150})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed read lengths'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'eCLIP'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed read lengths'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'Mint-ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed read lengths'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_valid_inter_length_sequencing_files(testapp,
                                                                         base_experiment,
                                                                         replicate_1_1,
                                                                         replicate_2_1,
                                                                         library_1,
                                                                         library_2,
                                                                         biosample_1,
                                                                         biosample_2,
                                                                         mouse_donor_1_6,
                                                                         mouse_donor_2,
                                                                         file_fastq_3,
                                                                         file_fastq_4,
                                                                         file_fastq_5):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 50})
    testapp.patch_json(file_fastq_5['@id'], {'read_length': 52})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'mixed read lengths'
               for error in collect_audit_errors(res))


def test_audit_experiment_DNase_mismatched_valid_inter_length_sequencing_files(
    testapp, base_experiment,
    replicate_1_1, replicate_2_1,
    library_1, library_2,
    biosample_1, biosample_2,
    mouse_donor_1_6,  mouse_donor_2,
    file_fastq_3, file_fastq_4,
        file_fastq_5):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 27})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 27})
    testapp.patch_json(file_fastq_5['@id'], {'read_length': 36})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'mixed read lengths'
               for error in collect_audit_errors(res))


def test_audit_experiment_long_rna_standards_crispr(testapp,
                                                    base_experiment,
                                                    replicate_1_1,
                                                    replicate_2_1,
                                                    library_1,
                                                    library_2,
                                                    biosample_1,
                                                    biosample_2,
                                                    mouse_donor_1_6,
                                                    file_fastq_3,
                                                    file_fastq_4,
                                                    file_bam_1_1,
                                                    file_bam_2_1,
                                                    file_tsv_1_2,
                                                    mad_quality_metric_1_2,
                                                    bam_quality_metric_1_1,
                                                    bam_quality_metric_2_1,
                                                    analysis_step_run_bam,
                                                    analysis_step_version_bam,
                                                    analysis_step_bam,
                                                    pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (paired-end, stranded)'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 5000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 10000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 10})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 100})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id'],
                                          'size_range': '>200'})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id'],
                                          'size_range': '>200'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'CRISPR genome editing followed by RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing spikeins' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_control_read_depth_encode4(testapp,
                                                   experiment_chip_control,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_bam_1_chip,
                                                   file_bam_2_chip,
                                                   file_tsv_1_2,
                                                   file_bam_control_chip,
                                                   chip_alignment_quality_metric_insufficient_read_depth,
                                                   chip_alignment_quality_metric_extremely_low_read_depth,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip,
                                                   file_fastq_1_chip):
    testapp.patch_json(chip_alignment_quality_metric_extremely_low_read_depth['@id'], {'quality_metric_of': [file_bam_control_chip['@id']]})
    testapp.patch_json(file_bam_control_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_control_chip['@id'], file_bam_1_chip['@id']],
                                             'dataset': experiment_chip_H3K27me3['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'step_run': analysis_step_run_chip_encode4['uuid'],
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(experiment_chip_H3K27me3['@id'], {'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment_chip_control['@id']]})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
        'control extremely low read depth' for error in collect_audit_errors(res))

    testapp.patch_json(file_fastq_1_chip['@id'], {
        'dataset': experiment_mint_chip['@id'],
        'replicate': replicate_1_mint_chip['@id']
    })
    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_tsv_1_2['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
        'control extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_peak_but_no_qc_encode4(testapp,
                                                   experiment_chip_control,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_fastq_control_chip,
                                                   file_fastq_1_chip,
                                                   file_bam_1_chip,
                                                   file_tsv_1_2,
                                                   chip_alignment_quality_metric_extremely_low_read_depth,
                                                   file_bam_control_chip,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(chip_alignment_quality_metric_extremely_low_read_depth['@id'], {'quality_metric_of': [file_bam_1_chip['@id']]})
    testapp.patch_json(file_fastq_control_chip['@id'], {'dataset': experiment_chip_control['@id']})
    testapp.patch_json(file_fastq_1_chip['@id'], {'controlled_by': [file_fastq_control_chip['@id']],
                                                  'dataset': experiment_chip_H3K27me3['@id']})
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id'],
                                                'dataset': experiment_chip_H3K27me3['@id'],
                                                'derived_from': [file_fastq_1_chip['@id']]})
    testapp.patch_json(file_bam_control_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id'],
                                                'dataset': experiment_chip_control['@id'],
                                                'derived_from': [file_fastq_control_chip['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_control_chip['@id'], file_bam_1_chip['@id']],
                                             'dataset': experiment_chip_H3K27me3['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'step_run': analysis_step_run_chip_encode4['uuid'],
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(experiment_chip_H3K27me3['@id'], {'possible_controls': [experiment_chip_control['@id']]})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
        'missing control quality metric' for error in collect_audit_errors(res))

    testapp.patch_json(file_fastq_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_tsv_1_2['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
        'missing control quality metric' for error in collect_audit_errors(res))


def test_audit_experiment_missing_control_alignment_chip_encode4(testapp,
                                                   experiment_chip_control,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_fastq_control_chip,
                                                   file_fastq_1_chip,
                                                   file_bam_1_chip,
                                                   file_tsv_1_2,
                                                   chip_alignment_quality_metric_extremely_low_read_depth,
                                                   file_bam_control_chip,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(chip_alignment_quality_metric_extremely_low_read_depth['@id'], {'quality_metric_of': [file_bam_1_chip['@id']]})
    testapp.patch_json(file_fastq_control_chip['@id'], {'dataset': experiment_chip_control['@id']})
    testapp.patch_json(file_fastq_1_chip['@id'], {'controlled_by': [file_fastq_control_chip['@id']],
                                                  'dataset': experiment_chip_H3K27me3['@id']})
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id'],
                                                'dataset': experiment_chip_H3K27me3['@id'],
                                                'derived_from': [file_fastq_1_chip['@id']]})
    testapp.patch_json(file_bam_control_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id'],
                                                'dataset': experiment_chip_control['@id'],
                                                'derived_from': [file_fastq_control_chip['@id']],
                                                'status': 'revoked'})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_control_chip['@id'], file_bam_1_chip['@id']],
                                             'dataset': experiment_chip_H3K27me3['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'step_run': analysis_step_run_chip_encode4['uuid'],
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(experiment_chip_H3K27me3['@id'], {'possible_controls': [experiment_chip_control['@id']],
                                                        'status': 'released',
                                                        'date_released': '2019-10-08'})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
    'missing control alignments' for error in collect_audit_errors(res))

    testapp.patch_json(file_fastq_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_tsv_1_2['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(experiment_mint_chip['@id'], {
        'status': 'released',
        'date_released': '2019-10-08'})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
        'missing control alignments' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_control_standards(
        testapp,
        base_experiment,
        experiment,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        mouse_donor_1_6,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        file_bam_2_1,
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_2_1['@id'],
                                                              file_bam_1_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'control_type': 'input library',
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'control extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_without_controls(
        testapp,
        base_experiment,
        experiment,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        mouse_donor_1_6,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        file_bam_2_1,
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'control_type': 'control',
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control alignments' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_with_controls_but_no_qc(
        testapp,
        base_experiment,
        experiment,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        mouse_donor_1_6,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        file_bam_2_1,
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'control_type': 'input library',
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control quality metric' for error in collect_audit_errors(res))
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [
        file_bam_1_1['@id'],
        file_bam_2_1['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing control quality metric' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_with_subsampled_controls(
        testapp,
        base_experiment,
        experiment,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        mouse_donor_1_6,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        file_bam_2_1,
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_H3K9me3):

    
    testapp.patch_json(analysis_step_bam['@id'], {'title': 'Alignment pooliing and subsampling step'})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1002,
                                                        'mapped': 1002,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Some subsampling pipeline'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'control_type': 'control',
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control alignments' for error in collect_audit_errors(res))
    testapp.patch_json(analysis_step_bam['@id'], {'title': 'Alignment pooling and subsampling step'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing control alignments' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_no_target_standards(testapp,
                                                       base_experiment,
                                                       replicate_1_1,
                                                       replicate_2_1,
                                                       library_1,
                                                       library_2,
                                                       biosample_1,
                                                       biosample_2,
                                                       mouse_donor_1_6,
                                                       file_fastq_3,
                                                       file_fastq_4,
                                                       file_bam_1_1,
                                                       file_bam_2_1,
                                                       file_tsv_1_2,
                                                       mad_quality_metric_1_2,
                                                       chip_seq_quality_metric,
                                                       chipseq_filter_quality_metric,
                                                       analysis_step_run_bam,
                                                       analysis_step_version_bam,
                                                       analysis_step_bam,
                                                       pipeline_bam):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 10000000,
                                                        'mapped': 10000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})

    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing target' for error in collect_audit_errors(res))


def test_audit_experiment_dnase_low_read_length(testapp,
                                                base_experiment,
                                                replicate_1_1,
                                                library_1,
                                                biosample_1,
                                                mouse_donor_1_6,
                                                file_fastq_3,
                                                file_bam_1_1,
                                                mad_quality_metric_1_2,
                                                chip_seq_quality_metric,
                                                analysis_step_run_bam,
                                                analysis_step_version_bam,
                                                analysis_step_bam,
                                                pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read length' for error in collect_audit_errors(res))


# duplication rate audit was removed from v54


def test_audit_experiment_out_of_date_analysis_added_fastq(testapp,
                                                           base_experiment,
                                                           replicate_1_1,
                                                           replicate_2_1,
                                                           file_fastq_3,
                                                           file_fastq_4,
                                                           file_bam_1_1,
                                                           file_bam_2_1,
                                                           experiment_mint_chip,
                                                           replicate_1_mint_chip):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'out of date analysis' for error in collect_audit_errors(res))

    testapp.patch_json(file_fastq_4['@id'], {
        'replicate': replicate_1_mint_chip['@id'],
        'dataset': experiment_mint_chip['@id']
    })
    testapp.patch_json(file_fastq_3['@id'], {
        'replicate': replicate_1_mint_chip['@id'],
        'dataset': experiment_mint_chip['@id']
    })
    testapp.patch_json(file_bam_1_1['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_2_1['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_out_of_date_analysis_removed_fastq(testapp,
                                                             base_experiment,
                                                             replicate_1_1,
                                                             replicate_2_1,
                                                             file_fastq_3,
                                                             file_fastq_4,
                                                             file_bam_1_1,
                                                             file_bam_2_1,
                                                             experiment_mint_chip):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'status': 'deleted'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'out of date analysis' for error in collect_audit_errors(res))

    testapp.patch_json(file_bam_1_1['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_2_1['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_not_out_of_date_analysis_DNase(testapp,
                                                         base_experiment,
                                                         replicate_1_1,
                                                         replicate_1_2,
                                                         file_fastq_3,
                                                         file_fastq_4,
                                                         file_bam_1_1,
                                                         file_bam_2_1):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_out_of_date_analysis_DNase(testapp,
                                                     base_experiment,
                                                     replicate_1_1,
                                                     replicate_1_2,
                                                     file_fastq_3,
                                                     file_fastq_4,
                                                     file_bam_1_1,
                                                     file_bam_2_1):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'replicate': replicate_1_1['@id'],
                                             'status': 'deleted'})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_out_of_date_analysis_ENCODE4_DNase(
        testapp,
        base_experiment,
        replicate_1_1,
        replicate_1_2,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        analysis_step_run_dnase_encode4,
        pipeline_dnase_encode4):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {
        'derived_from': [file_fastq_3['@id'], file_fastq_4['@id']],
        'step_run': analysis_step_run_dnase_encode4['@id']})
    testapp.patch_json(file_fastq_3['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'out of date analysis' for error in collect_audit_errors(res))
    testapp.patch_json(file_fastq_4['@id'], {'status': 'deleted'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_no_out_of_date_analysis(testapp,
                                                  base_experiment,
                                                  replicate_1_1,
                                                  replicate_2_1,
                                                  file_fastq_3,
                                                  file_fastq_4,
                                                  file_bam_1_1,
                                                  file_bam_2_1):
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'out of date analysis' for error in collect_audit_errors(res))


# def test_audit_experiment_modERN_control_missing_files() removed from v54
# def test_audit_experiment_modERN_experiment_missing_files() removed from v54


def test_audit_experiment_missing_genetic_modification(
        testapp,
        base_experiment,
        base_target,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        tag_antibody,
        biosample_1,
        biosample_2,
        donor_1,
        donor_2,
        k562):

    testapp.patch_json(biosample_1['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_2['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(
        replicate_1_1['@id'],
        {'library': library_1['@id'], 'antibody': tag_antibody['@id']}
    )
    testapp.patch_json(
        replicate_2_1['@id'],
        {'library': library_2['@id'], 'antibody': tag_antibody['@id']}
    )
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent genetic modification tags' for error in collect_audit_errors(res))


def test_audit_experiment_tagging_genetic_modification_characterization(
        testapp,
        construct_genetic_modification,
        gm_characterization,
        base_experiment,
        base_target,
        replicate_1_1,
        library_1,
        biosample_1,
        donor_1,
        k562):
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [construct_genetic_modification['@id']],
                                            'biosample_ontology': k562['uuid'],
                                            'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})  
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing genetic modification characterization' for error in collect_audit_errors(res))
    testapp.patch_json(gm_characterization['@id'], {'characterizes': construct_genetic_modification['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing genetic modification characterization' for error in collect_audit_errors(res))


def test_audit_experiment_tagging_biosample_characterization(
        testapp,
        construct_genetic_modification,
        interference_genetic_modification,
        biosample_characterization,
        base_experiment,
        base_target,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        donor_1,
        k562,
        award_encode4,
        wrangler,
    ):
    testapp.patch_json(biosample_1['@id'],
                       {'genetic_modifications': [interference_genetic_modification['@id']],
                        'biosample_ontology': k562['uuid'],
                        'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [interference_genetic_modification['@id']],
                        'biosample_ontology': k562['uuid'],
                        'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'],
                       {'assay_term_name': 'ChIP-seq',
                        'award': award_encode4['@id'],
                        'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing biosample characterization'
               for error in collect_audit_errors(res, ['WARNING']))
    testapp.patch_json(biosample_1['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing biosample characterization'
               for error in collect_audit_errors(res, ['ERROR']))                  
    testapp.patch_json(biosample_characterization['@id'],
                       {'characterizes': biosample_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing biosample characterization'
               for error in collect_audit_errors(res))
    # Has characterization but hasn't been reviewed as compliant
    assert any(
        error['category'] == 'missing compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )
    # Has compliant characterization
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing compliant biosample characterization'
        for error in collect_audit_errors(res)
    )
    # Has not compliant characterization
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'not compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'not compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )


def test_audit_experiment_pooled_biosample_no_characterization(
    testapp,
    biosample_pooled_from_not_characterized_biosamples,
    award_encode4,
    base_experiment,
    base_target,
    base_replicate,
    base_library,
):
    testapp.patch_json(
        base_experiment['@id'],
        {
            'assay_term_name': 'ChIP-seq',
            'award': award_encode4['@id'],
            'target': base_target['@id']
        }
    )
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(
        base_library['@id'],
        {'biosample': biosample_pooled_from_not_characterized_biosamples['@id']}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing biosample characterization'
        for error in collect_audit_errors(res, error_types=['ERROR'])
    )


def test_audit_experiment_pooled_biosample_partial_characterization(
    testapp,
    biosample_pooled_from_characterized_and_not_characterized_biosamples,
    award_encode4,
    base_experiment,
    base_target,
    base_replicate,
    base_library,
):
    testapp.patch_json(
        base_experiment['@id'],
        {
            'assay_term_name': 'ChIP-seq',
            'award': award_encode4['@id'],
            'target': base_target['@id']
        }
    )
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(
        base_library['@id'],
        {'biosample': biosample_pooled_from_characterized_and_not_characterized_biosamples['@id']}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing biosample characterization'
        for error in collect_audit_errors(res, error_types=['ERROR'])
    )


def test_audit_experiment_pooled_biosample_characterization(
    testapp,
    biosample_pooled_from_characterized_biosamples,
    award_encode4,
    base_experiment,
    base_target,
    base_replicate,
    base_library,
    biosample_characterization,
    biosample_characterization_no_review,
    wrangler,
):
    testapp.patch_json(
        base_experiment['@id'],
        {
            'assay_term_name': 'ChIP-seq',
            'award': award_encode4['@id'],
            'target': base_target['@id']
        }
    )
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(
        base_library['@id'],
        {'biosample': biosample_pooled_from_characterized_biosamples['@id']}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing biosample characterization'
        for error in collect_audit_errors(res)
    )
    # One compliant parent biosample
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )
    # One not compliant parent biosample
    testapp.patch_json(
        biosample_characterization_no_review['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'not compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'not compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )
    # Both parent biosamples are compliant
    testapp.patch_json(
        biosample_characterization_no_review['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] not in [
            'missing biosample characterization',
            'missing compliant biosample characterization',
            'not compliant biosample characterization',
        ]
        for error in collect_audit_errors(res, ['ERROR'])
    )


@pytest.mark.parametrize(
    'relationship',
    [
        'part_of',
        'originated_from'
    ])
def test_biosample_characterization_parent_relationship(
        testapp,
        relationship,
        construct_genetic_modification,
        biosample_characterization,
        base_experiment,
        base_target,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        base_biosample,
        donor_1,
        k562,
        award_encode4,
        wrangler,
        treatment_5
):
    # Parent biosamples via part_of or originated_from can be checked for biosample
    # characterizations if ontology, applied_modifications, and treatments match the child
    testapp.patch_json(biosample_1['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']],
                        'biosample_ontology': k562['uuid'],
                        'donor': donor_1['@id'],
                        relationship: base_biosample['@id']})
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']],
                        'biosample_ontology': k562['uuid'],
                        'donor': donor_1['@id'],
                        relationship: base_biosample['@id']})
    testapp.patch_json(base_biosample['@id'],
                       {'biosample_ontology': k562['uuid'],
                       'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'],
                       {'assay_term_name': 'ChIP-seq',
                        'award': award_encode4['@id'],
                        'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing biosample characterization'
               for error in collect_audit_errors(res, ['ERROR']))
    # Parent biosample characterization not reviewed
    testapp.patch_json(biosample_characterization['@id'],
                       {'characterizes': base_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing biosample characterization'
               for error in collect_audit_errors(res))
    assert any(
        error['category'] == 'missing compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )
    # Parent has compliant characterization
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing compliant biosample characterization'
        for error in collect_audit_errors(res)
    )
    # Parent has not compliant characterization
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'lab': base_experiment['lab'],
                'reviewed_by': wrangler['@id'],
                'status': 'not compliant'
            }
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'not compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )
    # If treatments or modifications differ between child and parent, parent won't be queried
    testapp.patch_json(biosample_1['@id'],
                       {'treatments': [treatment_5['@id']]})
    testapp.patch_json(biosample_2['@id'],
                       {'treatments': [treatment_5['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )
    assert all(
        error['category'] != 'not compliant biosample characterization'
        for error in collect_audit_errors(res)
    )
    # Adding the matching treatment to the parent means it is checked again
    testapp.patch_json(base_biosample['@id'],
                       {'treatments': [treatment_5['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'not compliant biosample characterization'
        for error in collect_audit_errors(res, ['ERROR'])
    )


def test_audit_experiment_missing_unfiltered_bams(testapp,
                                                  base_experiment,
                                                  replicate_1_1,
                                                  replicate_2_1,
                                                  file_fastq_3,
                                                  file_bam_1_1,
                                                  file_bam_2_1,
                                                  analysis_step_run_bam,
                                                  analysis_step_version_bam,
                                                  analysis_step_bam,
                                                  pipeline_bam):

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_3['@id']],
                                             'assembly': 'hg19',
                                             'output_type': 'unfiltered alignments'})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing unfiltered alignments' for error in collect_audit_errors(res))

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'Mint-ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing unfiltered alignments' for error in collect_audit_errors(res))


def test_audit_experiment_wrong_modification(
        testapp,
        base_experiment,
        base_target,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        tag_antibody,
        biosample_1,
        biosample_2,
        donor_1,
        donor_2,
        construct_genetic_modification,
        k562):

    testapp.patch_json(construct_genetic_modification['@id'],
                       {'modified_site_by_target_id': base_target['@id'],
                        'introduced_tags': [{'name': 'FLAG', 'location': 'internal'}]})
    testapp.patch_json(biosample_1['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_2['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(
        replicate_1_1['@id'],
        {'library': library_1['@id'], 'antibody': tag_antibody['@id']}
    )
    testapp.patch_json(
        replicate_2_1['@id'],
        {'library': library_2['@id'], 'antibody': tag_antibody['@id']}
    )
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent genetic modification tags' for error in collect_audit_errors(res))

    testapp.patch_json(construct_genetic_modification['@id'],
                       {'introduced_tags': [{'name': 'eGFP', 'location': 'internal'}]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'inconsistent genetic modification tags'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_chip_seq_mapped_read_length(testapp,
                                                      base_experiment,
                                                      experiment_mint_chip,
                                                      file_fastq_3,
                                                      file_fastq_4,
                                                      file_bam_1_1,
                                                      file_bam_2_1,
                                                      file_tsv_1_2):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 100})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 130})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_2_1['@id'],
                                                              file_bam_1_1['@id']],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent mapped reads lengths' for error in collect_audit_errors(res))

    testapp.patch_json(file_fastq_3['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_fastq_4['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_2_1['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_tsv_1_2['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent mapped reads lengths' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_consistent_mapped_read_length(
        testapp,
        base_experiment,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        file_bam_2_1,
        file_tsv_1_2):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 124})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 130})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_2_1['@id'],
                                                              file_bam_1_1['@id']],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'inconsistent mapped reads lengths' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_read_count(
        testapp,
        base_experiment,
        experiment_mint_chip,
        file_fastq_3,
        file_fastq_4,
        replicate_1_mint_chip):
    testapp.patch_json(file_fastq_3['@id'], {'read_count': 124})
    testapp.patch_json(file_fastq_4['@id'], {'read_count': 134})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read count' for error in collect_audit_errors(res))
    testapp.patch_json(file_fastq_3['@id'], {'read_count': 100000000})
    testapp.patch_json(file_fastq_4['@id'], {'read_count': 100000000})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'low read count' for error in collect_audit_errors(res))

    testapp.patch_json(file_fastq_4['@id'], {
        'replicate': replicate_1_mint_chip['@id'],
        'dataset': experiment_mint_chip['@id']
    })
    testapp.patch_json(file_fastq_3['@id'], {
        'replicate': replicate_1_mint_chip['@id'],
        'dataset': experiment_mint_chip['@id']
    })
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert all(error['category'] !=
               'low read count' for error in collect_audit_errors(res))
    testapp.patch_json(file_fastq_3['@id'], {'read_count': 124})
    testapp.patch_json(file_fastq_4['@id'], {'read_count': 134})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read count' for error in collect_audit_errors(res))


def test_audit_experiment_with_biosample_missing_nih_consent(testapp, experiment, replicate_url,
                                                             library_url, biosample, encode4_award):
    testapp.patch_json(experiment['@id'], {'award': encode4_award['@id']})
    r = testapp.get(experiment['@id'] + '@@index-data')
    audits = r.json['audit']
    assert any(
        [
            detail['category'] == 'missing nih_institutional_certification'
            for audit in audits.values() for detail in audit
        ]
    )


def test_audit_experiment_with_biosample_not_missing_nih_consent(testapp, experiment, replicate,
                                                                 library, biosample, encode4_award):
    testapp.patch_json(experiment['@id'], {'award': encode4_award['@id']})
    testapp.patch_json(biosample['@id'], {'nih_institutional_certification': 'NICABC123'})
    r = testapp.get(experiment['@id'] + '@@index-data')
    audits = r.json['audit']
    assert all(
        [
            detail['category'] != 'missing nih_institutional_certification'
            for audit in audits.values() for detail in audit
        ]
    )


def test_audit_fcc_experiment_nih_consent(
        testapp,
        experiment,
        replicate,
        library,
        biosample,
        encode4_award,
    ):
    testapp.patch_json(encode4_award['@id'], {'component': 'functional characterization'})
    testapp.patch_json(experiment['@id'], {'award': encode4_award['@id']})
    r = testapp.get(experiment['@id'] + '@@index-data')
    audits = r.json['audit']
    assert not any(
        [
            detail['category'] == 'missing nih_institutional_certification'
            for audit in audits.values() for detail in audit
        ]
    )


def test_audit_experiment_computational_award_nih_consent(testapp, experiment, encode4_award):
    testapp.patch_json(encode4_award['@id'], {'component': 'computational analysis'})
    testapp.patch_json(experiment['@id'], {'award': encode4_award['@id']})
    r = testapp.get(experiment['@id'] + '@@index-data')
    audits = r.json['audit']
    assert not any(
        [
            detail['category'] == 'missing nih_institutional_certification'
            for audit in audits.values() for detail in audit
        ]
    )


def test_is_matching_biosample_control(testapp, biosample, ctrl_experiment):
    from encoded.audit.experiment import is_matching_biosample_control
    exp = testapp.get(ctrl_experiment['@id'] + '@@index-data')
    exp_embedded = exp.json['embedded']
    bio = testapp.get(biosample['@id'] + '@@index-data')
    bio_embedded = bio.json['embedded']
    assert is_matching_biosample_control(exp_embedded, bio_embedded['biosample_ontology']['term_id']) == False
    testapp.patch_json(biosample['@id'], {'biosample_ontology': ctrl_experiment['biosample_ontology']})
    bio = testapp.get(biosample['@id'] + '@@index-data')
    bio_embedded = bio.json['embedded']
    assert is_matching_biosample_control(exp_embedded, bio_embedded['biosample_ontology']['term_id']) == True


def test_audit_experiment_histone_characterized_no_primary(testapp,
                                                           base_experiment,
                                                           wrangler,
                                                           base_antibody,
                                                           base_replicate,
                                                           base_library,
                                                           base_biosample,
                                                           target_H3K9me3,
                                                           mouse_H3K9me3,
                                                           base_antibody_characterization2,
                                                           mouse,
                                                           mel):
    # Supporting antibody only have secondary characterizations
    testapp.patch_json(base_biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': mel['uuid'],
                                                'target': mouse_H3K9me3['@id']})
    base_antibody['targets'] = [mouse_H3K9me3['@id']]
    no_primary_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': no_primary_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(
        base_antibody_characterization2['@id'],
        {'target': mouse_H3K9me3['@id'],
            'characterizes': no_primary_antibody['@id'],
            'status': 'not compliant',
            'reviewed_by': wrangler['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'antibody not characterized to standard'
               for error in collect_audit_errors(res))


def test_audit_experiment_tag_target(testapp, experiment, ctcf):
    tag_target = testapp.post_json(
        '/target',
        {
            'genes': [ctcf['uuid']],
            'modifications': [{'modification': 'eGFP'}],
            'label': 'eGFP-CTCF',
            'investigated_as': ['other context']
        }
    ).json['@graph'][0]
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': tag_target['@id']})
    audits = testapp.get(experiment['@id'] + '@@index-data').json['audit']
    assert any(detail['category'] == 'inconsistent experiment target'
               for audit in audits.values() for detail in audit)


def test_audit_experiment_inconsist_mod_target(testapp, experiment,
                                               library_url, replicate_url, biosample, ctcf,
                                               construct_genetic_modification):
    tag_target = testapp.post_json(
        '/target',
        {
            'genes': [ctcf['uuid']],
            'modifications': [{'modification': 'eGFP'}],
            'label': 'eGFP-CTCF',
            'investigated_as': ['other context']
        }
    ).json['@graph'][0]
    testapp.patch_json(
        biosample['@id'],
        {'genetic_modifications': [construct_genetic_modification['@id']]}
    )
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': tag_target['@id']})
    audits = testapp.get(experiment['@id'] + '@@index-data').json['audit']
    assert any(detail['category'] == 'inconsistent genetic modification targets'
               for audit in audits.values() for detail in audit)


def test_audit_experiment_chip_seq_control_target_failures(
    testapp,
    base_experiment,
    experiment,
    file_fastq_3,
    file_bam_1_1,
    file_tsv_1_2,
    analysis_step_run_bam,
    pipeline_bam,
    target_H3K9me3,
):
    testapp.patch_json(
        base_experiment['@id'],
        {
            'target': target_H3K9me3['@id'],
            'possible_controls': [experiment['@id']],
            'assay_term_name': 'ChIP-seq',
        }
    )
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'derived_from': [file_bam_1_1['@id']],
            'dataset': base_experiment['@id'],
            'file_format_type': 'narrowPeak',
            'file_format': 'bed',
            'output_type': 'peaks',
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'step_run': analysis_step_run_bam['@id'],
            'dataset': experiment['@id'],
            'derived_from': [file_fastq_3['@id']]
        }
    )

    testapp.patch_json(
        experiment['@id'],
        {
            'target': target_H3K9me3['@id'],
            'assay_term_name': 'ChIP-seq'
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing control_type of control experiment'
        for error in collect_audit_errors(res)
    )
    assert all(
        error['category'] != 'improper control_type of control experiment'
        for error in collect_audit_errors(res)
    )
    assert any(
        error['category'] == 'unexpected target of control experiment'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        experiment['@id'],
        {
            'control_type': 'control',
            'assay_term_name': 'ChIP-seq'
        }
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing control_type of control experiment'
        for error in collect_audit_errors(res)
    )
    assert any(
        error['category'] == 'improper control_type of control experiment'
        for error in collect_audit_errors(res)
    )
    assert any(
        error['category'] == 'unexpected target of control experiment'
        for error in collect_audit_errors(res)
    )
    ctrl_exp = testapp.get(experiment['@id'] + '@@edit').json
    ctrl_exp.pop('target')
    testapp.put_json(experiment['@id'], ctrl_exp)
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'unexpected target of control experiment'
        for error in collect_audit_errors(res)
    )


def test_audit_experiment_missing_queried_RNP_size_range(
    testapp,
    base_experiment,
    replicate_1_1,
    library_1
):
    testapp.patch_json(base_experiment['@id'], {
        'assay_term_name': 'eCLIP'
        })
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing queried_RNP_size_range'
               for error in collect_audit_errors(res))


def test_audit_experiment_mixed_queried_RNP_size_range(
    testapp,
    base_experiment,
    replicate_1_1,
    replicate_2_1,
    library_1,
    library_2
):
    testapp.patch_json(base_experiment['@id'], {
        'assay_term_name': 'eCLIP'
        })
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {
        'library': library_2['@id'],
        'experiment': base_experiment['@id']
        })
    testapp.patch_json(library_1['@id'], {'queried_RNP_size_range': '150-200'})
    testapp.patch_json(library_2['@id'], {'queried_RNP_size_range': '200-400'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed queried_RNP_size_range'
               for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_queried_RNP_size_range(
    testapp,
    base_experiment,
    experiment,
    replicate_1_1,
    replicate_2_1,
    library_1,
    library_2
):
    testapp.patch_json(base_experiment['@id'], {
        'assay_term_name': 'eCLIP',
        'possible_controls': [experiment['@id']]
        })
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'eCLIP'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {
        'library': library_2['@id'],
        'experiment': experiment['@id']
        })
    testapp.patch_json(library_1['@id'], {'queried_RNP_size_range': '150-200'})
    testapp.patch_json(library_2['@id'], {'queried_RNP_size_range': '200-400'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent queried_RNP_size_range'
               for error in collect_audit_errors(res))


def test_audit_experiment_lacking_processed_data(
    testapp,
    base_experiment,
    experiment,
    file_fastq,
    file_bam
    ):

    testapp.patch_json(file_fastq['@id'], {
        'dataset': base_experiment['@id'],
        })
    testapp.patch_json(file_bam['@id'], {
        'dataset': base_experiment['@id'],
        })
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(warning['category'] != 'lacking processed data'
        for warning in collect_audit_errors(res))
    testapp.patch_json(file_bam['@id'], {
        'dataset': experiment['@id']
        })
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(warning['category'] == 'lacking processed data'
        for warning in collect_audit_errors(res))
    testapp.patch_json(file_fastq['@id'], {
        'dataset': experiment['@id']
        })
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(warning['category'] == 'lacking processed data'
        for warning in collect_audit_errors(res))


def test_audit_experiment_control(testapp, base_matched_set, ChIP_experiment, experiment, base_experiment):
    ctrl = testapp.patch_json(base_matched_set['@id'], {'related_datasets': [experiment['@id'],
                                                                        base_experiment['@id']]})
    res = testapp.get(ChIP_experiment['@id'] + '@@index-data')
    assert (error['category'] == 'inconsistent control' for error in collect_audit_errors(res))
    ctrl = testapp.patch_json(base_matched_set['@id'], {'related_datasets': [experiment['@id']]})
    res = testapp.get(ChIP_experiment['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent control' for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_analysis_files(
    testapp,
    experiment_with_analysis,
    experiment_with_analysis_2,
    analysis_1,
    analysis_2,
    analysis_released,
    file_bam_1_1,
    file_bam_2_1,
    bigWig_file,
    bam_file
):
    # No inconsistencies, all files in analyses and all analyses associated with dataset
    testapp.patch_json(file_bam_1_1['@id'], {
        'dataset': experiment_with_analysis['@id'],
        })
    testapp.patch_json(file_bam_2_1['@id'], {
        'dataset': experiment_with_analysis['@id'],
        })
    testapp.patch_json(bam_file['@id'], {
        'dataset': experiment_with_analysis['@id'],
        })
    testapp.patch_json(experiment_with_analysis['@id'], {
        'analyses': [analysis_1['@id'], analysis_2['@id'], analysis_released['@id']]
        })
    res = testapp.get(experiment_with_analysis['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent analysis files' for error in collect_audit_errors(res))
    # Processed file not in any analysis
    testapp.patch_json(bigWig_file['@id'], {
        'dataset': experiment_with_analysis['@id'],
        })
    res = testapp.get(experiment_with_analysis['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analysis files' for error in collect_audit_errors(res))
    # Files in analysis belonging to a different dataset
    testapp.patch_json(file_bam_1_1['@id'], {
        'dataset': experiment_with_analysis_2['@id'],
        })
    testapp.patch_json(file_bam_2_1['@id'], {
        'dataset': experiment_with_analysis_2['@id'],
        })
    res = testapp.get(experiment_with_analysis_2['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analysis files' for error in collect_audit_errors(res))
    # Deleted files are excluded from processed data
    testapp.patch_json(file_bam_1_1['@id'], {
        'status': 'deleted'
        })
    testapp.patch_json(file_bam_2_1['@id'], {
        'status': 'deleted'
        })
    testapp.patch_json(bam_file['@id'], {
        'dataset': experiment_with_analysis_2['@id'],
        'status': 'deleted'
        })
    res = testapp.get(experiment_with_analysis_2['@id'] + '@@index-data')
    print(res.json['audit'])
    assert not any(error['category'] == 'inconsistent analysis files' for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_genetic_modifications(
        testapp,
        construct_genetic_modification,
        interference_genetic_modification,
        base_experiment,
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
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))
    # biosamples with the same genetic modifications
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [construct_genetic_modification['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))
    # biosamples with different genetic modifications
    testapp.patch_json(biosample_2['@id'],
                       {'genetic_modifications': [interference_genetic_modification['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent genetic modifications' for error in collect_audit_errors(res))


def test_audit_experiment_average_fragment_size(testapp, base_experiment, base_replicate, base_library):
    # average_fragment_size may stand in for size_range, behavior should match
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_library['@id'], {'average_fragment_size': 220})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    res_errors = collect_audit_errors(res)
    assert any(error['category'] == 'missing spikeins'
               for error in res_errors)
    assert 'missing RNA fragment size' not in res_errors


def test_audit_experiment_mixed_strand_specificity_libraries(
        testapp, base_experiment, replicate_1_1, replicate_2_1,
        library_1, library_2
        ):
    # https://encodedcc.atlassian.net/browse/ENCD-5554
    testapp.patch_json(library_1['@id'], {'strand_specificity': 'reverse'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed strand specificities'
               for error in collect_audit_errors(res))

    testapp.patch_json(library_2['@id'], {'strand_specificity': 'strand-specific'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed strand specificities'
               for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_analysis_status(testapp, experiment_with_analysis,
                                                       analysis_released, analysis_released_2,
                                                       analysis_1, experiment_rna):
    # https://encodedcc.atlassian.net/browse/ENCD-5705
    # Released analysis objects are disallowed in non-released datasets
    testapp.patch_json(experiment_with_analysis['@id'],
                       {"analyses": [analysis_released["@id"]]})
    res = testapp.get(experiment_with_analysis['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analysis status'
               and 'not released' in error['detail']
               for error in collect_audit_errors(res))
    # Released datasets must have a released analysis
    testapp.patch_json(
        experiment_with_analysis['@id'], {'status': 'released', 'date_released': '2021-01-01'})
    testapp.patch_json(
        experiment_with_analysis['@id'], {"analyses": [analysis_1["@id"]]})
    res = testapp.get(experiment_with_analysis['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analysis status'
               and 'lacks a released analysis' in error['detail']
               for error in collect_audit_errors(res))
    # Multiple released analyses in a dataset is disallowed
    testapp.patch_json(
        experiment_with_analysis['@id'], {
            "analyses": [analysis_released["@id"], analysis_released_2["@id"]]})
    res = testapp.get(experiment_with_analysis['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analysis status'
               and 'released analyses' in error['detail']
               for error in collect_audit_errors(res))
    # Datasets lacking a released analysis (no analyses at all) are flagged
    res = testapp.get(experiment_rna['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analysis status'
               and 'lacks a released analysis' in error['detail']
               for error in collect_audit_errors(res))


def test_audit_experiment_mixed_biosamples_replication_type(testapp, base_experiment, biosample_1,
                                                            biosample_2, base_replicate,
                                                            library_no_biosample):
    # https://encodedcc.atlassian.net/browse/ENCD-5706
    testapp.patch_json(library_no_biosample['@id'], {
        'mixed_biosamples': [biosample_1['@id'], biosample_2['@id']]})
    testapp.patch_json(base_replicate['@id'], {'library': library_no_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'undetermined replication_type'
               for error in collect_audit_errors(res))


def test_audit_experiment_single_cell_libraries(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_library['@id'], {'barcode_details': [{'barcode': 'ATTTCGC'}]})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent barcode details'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'single-cell RNA sequencing assay'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent barcode details'
               for error in collect_audit_errors(res))
