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


def test_audit_experiment_replicated(testapp, base_experiment, base_replicate, base_library, a549, single_cell):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'unreplicated experiment' and error['level_name'] == 'INTERNAL_ACTION'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'biosample_ontology': a549['uuid']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'unreplicated experiment' and error['level_name'] == 'NOT_COMPLIANT'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'biosample_ontology': single_cell['uuid']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))
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


def test_audit_experiment_geo_submission(testapp, base_experiment):
    testapp.patch_json(
        base_experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'experiment not submitted to GEO'
               for error in collect_audit_errors(res))


def test_audit_experiment_biosample_match(testapp, base_experiment,
                                          base_biosample, base_replicate,
                                          base_library, h1, ileum):
    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': h1['uuid']})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'biosample_ontology': ileum['uuid']})
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
                                                         library_no_biosample):
    testapp.patch_json(base_replicate['@id'], {'library': library_no_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing biosample'
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


def test_audit_experiment_rampage_standards(testapp,
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
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 100})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 100})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 100})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RAMPAGE (paired-end, stranded)'})

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
                                                'assay_term_name': 'RAMPAGE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_small_rna_standards(testapp,
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
                                             'Small RNA-seq single-end pipeline'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 26000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 26000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 1000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 1000000})
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
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_MAD_long_rna_standards(testapp,
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

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 29000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 38000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 1})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 1})
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
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low replicate concordance' for error in collect_audit_errors(res))


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
    assert any(
        error['category'] ==
        'insufficient read depth' for error in collect_audit_errors(res)) and \
        any(error['category'] ==
            'missing spikeins' for error in collect_audit_errors(res))


def test_audit_experiment_long_rna_standards(testapp,
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
                                             file_tsv_1_1,
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

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 1000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 38000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 10})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 30})
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'quality_metric_of': [
                                                       file_tsv_1_1['@id'],
                                                       file_tsv_1_2['@id']]})
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
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_micro_rna_standards(
    testapp,
    micro_rna_experiment,
    spearman_correlation_quality_metric,
    micro_rna_quantification_quality_metric_1_2,
    micro_rna_mapping_quality_metric_2_1,
):
    expected_audits = [
        'borderline number of aligned reads',
        'borderline microRNAs expressed',
        'insufficient replicate concordance',
    ]
    errors = collect_audit_errors(micro_rna_experiment)
    for audit in expected_audits:
        assert any(
            error['category'] == audit for error in errors
        )
    # Test that audits are not triggered when patching qc to safe values
    testapp.patch_json(spearman_correlation_quality_metric['@id'], {'Spearman correlation': 0.99})
    testapp.patch_json(micro_rna_quantification_quality_metric_1_2['@id'], {'expressed_mirnas': 1000000})
    testapp.patch_json(micro_rna_mapping_quality_metric_2_1['@id'], {'aligned_reads': 10000000})
    res = testapp.get(micro_rna_experiment.json['object']['@id'] + '@@index-data')
    errors = collect_audit_errors(res)
    for audit in expected_audits:
        assert not any(
            error['category'] == audit for error in errors
        )


def test_audit_experiment_micro_rna_standards_M21(
    testapp,
    micro_rna_experiment,
    file_tsv_1_1,
    file_tsv_1_2,
):
    testapp.patch_json(file_tsv_1_1['@id'], {'genome_annotation': 'M21'})
    testapp.patch_json(file_tsv_1_2['@id'], {'genome_annotation': 'M21'})
    res = testapp.get(micro_rna_experiment.json['object']['@id'] + '@@index-data')
    expected_audits = [
        'borderline number of aligned reads',
        'borderline microRNAs expressed',
        'insufficient replicate concordance',
    ]
    errors = collect_audit_errors(res)
    for audit in expected_audits:
        assert any(
            error['category'] == audit for error in errors
        )


def test_audit_experiment_long_read_rna_standards(
    testapp,
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
    file_tsv_1_1,
    file_tsv_1_2,
    spearman_correlation_quality_metric,
    long_read_rna_quantification_quality_metric_1_2,
    long_read_rna_mapping_quality_metric_2_1,
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    pipeline_bam,
):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})
    testapp.patch_json(
        file_bam_1_1['@id'],
        {'step_run': analysis_step_run_bam['@id'], 'assembly': 'mm10'}
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {'step_run': analysis_step_run_bam['@id'], 'assembly': 'mm10', 'output_type': 'unfiltered alignments'}
    )
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {'output_type': 'transcript quantifications'}
    )
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {'output_type': 'transcript quantifications'}
    )
    testapp.patch_json(
        pipeline_bam['@id'],
        {'title': 'Long read RNA-seq pipeline'})
    testapp.patch_json(
        spearman_correlation_quality_metric['@id'],
        {'quality_metric_of': [file_tsv_1_1['@id'], file_tsv_1_2['@id']]}
    )
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
    testapp.patch_json(
        base_experiment['@id'],
        {'status': 'released', 'date_released': '2016-01-01', 'assay_term_name': 'long read RNA-seq'}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    expected_audits = [
        'borderline replicate concordance',
        'borderline sequencing depth',
        'insufficient mapping rate',
        'borderline genes detected',
    ]
    errors = collect_audit_errors(res)
    for audit in expected_audits:
        assert any(
            error['category'] == audit for error in errors
        )

 
def test_audit_experiment_chip_seq_standards_read_depth_encode4_wcontrol(testapp,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_fastq_1_chip,
                                                   file_bam_1_chip,
                                                   file_bam_2_chip,
                                                   chip_alignment_quality_metric_extremely_low_read_depth,
                                                   chip_alignment_quality_metric_insufficient_read_depth,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))

    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_read_depth_encode4_wcontrol_wmapped_run_type(testapp,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_fastq_1_chip,
                                                   file_bam_1_chip,
                                                   file_bam_2_chip,
                                                   chip_alignment_quality_metric_extremely_low_read_depth_no_read1_read2,
                                                   chip_alignment_quality_metric_insufficient_read_depth_no_read1_read2,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(file_bam_1_chip['@id'], {'mapped_run_type': 'paired-ended',
                                                'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'mapped_run_type': 'single-ended',
                                                'step_run': analysis_step_run_chip_encode4['@id']})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))

    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_missing_read_depth_encode4_wcontrol(testapp,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_fastq_control_chip,
                                                   file_fastq_1_chip,
                                                   file_bam_1_chip,
                                                   file_bam_2_chip,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing read depth' for error in collect_audit_errors(res))

    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_library_complexity_encode4_wcontrol(testapp,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_bam_1_chip,
                                                   chip_library_quality_metric_severe_bottlenecking_poor_complexity,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
               'severe bottlenecking' for error in collect_audit_errors(res))
    assert any(error['category'] ==
               'poor library complexity' for error in collect_audit_errors(res))

    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'severe bottlenecking' for error in collect_audit_errors(res))
    assert any(error['category'] ==
               'poor library complexity' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_rsc_nsc(testapp,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   file_bam_1_chip,
                                                   chip_align_enrich_quality_metric,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    audit_errors = collect_audit_errors(res)
    assert any(error['category'] ==
               'negative NSC' for error in audit_errors)
    assert all(error['category'] !=
               'negative RSC' for error in audit_errors)

    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    audit_errors = collect_audit_errors(res)
    assert any(error['category'] ==
               'negative NSC' for error in audit_errors)
    assert all(error['category'] !=
               'negative RSC' for error in audit_errors)


def test_audit_experiment_chip_seq_standards_idr_encode4_wcontrol(testapp,
                                                   experiment_chip_H3K27me3,
                                                   experiment_mint_chip,
                                                   replicate_1_chip,
                                                   replicate_2_chip,
                                                   file_bam_1_chip,
                                                   file_bed_narrowPeak_chip_peaks,
                                                   file_bed_narrowPeak_chip_peaks2,
                                                   file_bed_narrowPeak_chip_background,
                                                   file_bed_narrowPeak_chip_background2,
                                                   enc3_chip_idr_quality_metric_insufficient_replicate_concordance,
                                                   chip_replication_quality_metric_borderline_replicate_concordance,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4,
                                                   replicate_1_mint_chip,
                                                   replicate_2_mint_chip):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_background['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_peaks['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(chip_replication_quality_metric_borderline_replicate_concordance['@id'], {'quality_metric_of': [file_bed_narrowPeak_chip_peaks['@id']]})
    testapp.patch_json(experiment_chip_H3K27me3['@id'], {'replicates': [replicate_1_chip['@id'], replicate_2_chip['@id']]})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
               'borderline replicate concordance' for error in collect_audit_errors(res))

    testapp.patch_json(file_bed_narrowPeak_chip_background2['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_peaks2['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(enc3_chip_idr_quality_metric_insufficient_replicate_concordance['@id'], {'quality_metric_of': [file_bed_narrowPeak_chip_peaks2['@id']]})
    res = testapp.get(experiment_chip_H3K27me3['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in collect_audit_errors(res))
    
    testapp.patch_json(file_bam_1_chip['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_background['@id'], {'dataset': experiment_mint_chip['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_peaks['@id'], {'dataset': experiment_mint_chip['@id']})
    res = testapp.get(experiment_mint_chip['@id'] + '@@index-data')
    assert any(error['category'] ==
               'borderline replicate concordance' for error in collect_audit_errors(res))


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


def test_audit_experiment_chip_seq_standards_control_missing_read_depth_encode4(testapp,
                                                   experiment_chip_control,
                                                   file_bam_control_chip,
                                                   analysis_step_run_chip_encode4,
                                                   analysis_step_version_chip_encode4,
                                                   analysis_step_chip_encode4,
                                                   pipeline_chip_encode4):
    testapp.patch_json(file_bam_control_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    res = testapp.get(experiment_chip_control['@id'] + '@@index-data')
    assert any(error['category'] ==
        'missing read depth' for error in collect_audit_errors(res))


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
                                                'derived_from': [file_fastq_control_chip['@id']]})
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


def test_audit_experiment_long_rna_standards_encode2(testapp,
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
                                                     file_tsv_1_1,
                                                     file_tsv_1_2,
                                                     mad_quality_metric_1_2,
                                                     bam_quality_metric_1_1,
                                                     bam_quality_metric_2_1,
                                                     analysis_step_run_bam,
                                                     analysis_step_version_bam,
                                                     analysis_step_bam,
                                                     pipeline_bam,
                                                     encode2_award):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (paired-end, stranded)'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 21000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 38000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 10})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 30})
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'quality_metric_of': [
                                                       file_tsv_1_1['@id'],
                                                       file_tsv_1_2['@id']]})
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
                                                'assay_term_name': 'RNA-seq',
                                                'award': encode2_award['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_depth(testapp,
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
                                                   analysis_step_run_bam,
                                                   analysis_step_version_bam,
                                                   analysis_step_bam,
                                                   pipeline_bam,
                                                   target_H3K27ac):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id'],
                                                                              file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 30000000,
                                                        'mapped': 30000000,
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K27ac['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_redacted_alignments_standards_depth(
    testapp,
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
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    pipeline_bam,
    target_H3K27ac):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id'],
                                                                              file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 30000000,
                                                        'mapped': 30000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'output_type': 'redacted alignments',
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'output_type': 'redacted alignments',
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K27ac['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read depth' for error in collect_audit_errors(res))


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


def test_audit_experiment_chip_seq_peaks_with_matched_set(
        testapp,
        base_experiment,
        experiment,
        treatment_time_series,
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
    
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id'], file_bam_2_1['@id']],
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
    testapp.patch_json(treatment_time_series['@id'], {'related_datasets': [experiment['@id']]})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [treatment_time_series['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': treatment_time_series['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control quality metric' for error in collect_audit_errors(res))
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [
        file_bam_1_1['@id'],
        file_bam_2_1['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing control quality metric' for error in collect_audit_errors(res))


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


def test_audit_experiment_chip_seq_standards(testapp,
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
                                             analysis_step_run_bam,
                                             analysis_step_version_bam,
                                             analysis_step_bam,
                                             pipeline_bam,
                                             target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 10000000,
                                                        'mapped': 10000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']],
                                             'output_type': 'unfiltered alignments'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_encode2(testapp,
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
                                                     analysis_step_run_bam,
                                                     analysis_step_version_bam,
                                                     analysis_step_bam,
                                                     pipeline_bam,
                                                     target_H3K9me3,
                                                     encode2_award):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 146000000,
                                                        'mapped': 146000000,
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq',
                                                'award': encode2_award['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'insufficient read depth' for error in collect_audit_errors(res))


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


def test_audit_experiment_chip_seq_library_complexity_standards(testapp,
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
                                                                pipeline_bam,
                                                                target_H3K9me3):
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'severe bottlenecking' for error in collect_audit_errors(res))


def test_audit_experiment_dnase_low_spot_score(testapp,
                                               base_experiment,
                                               replicate_1_1,
                                               library_1,
                                               biosample_1,
                                               mouse_donor_1_6,
                                               file_fastq_3,
                                               file_bam_1_1,
                                               mad_quality_metric_1_2,
                                               hotspot_quality_metric,
                                               analysis_step_run_bam,
                                               analysis_step_version_bam,
                                               analysis_step_bam,
                                               file_tsv_1_1,
                                               pipeline_bam):
    testapp.patch_json(file_tsv_1_1['@id'], {'output_type': 'hotspots'})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
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
               'low spot score' for error in collect_audit_errors(res))


def test_audit_experiment_dnase_seq_low_read_depth(testapp,
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
               'extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_wgbs_coverage(testapp,
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
                                         file_bed_methyl,
                                         chip_seq_quality_metric,
                                         analysis_step_run_bam,
                                         analysis_step_version_bam,
                                         analysis_step_bam,
                                         pipeline_bam):

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'WGBS paired-end pipeline'})

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bed_methyl['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 30000000,
                                                        'mapped': 30000000,
                                                        'read1': 100, 'read2': 100})
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
                                                'assay_term_name': 'whole-genome shotgun bisulfite sequencing'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low coverage' for error in collect_audit_errors(res))
   
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


def test_audit_experiment_dnase_low_correlation(testapp,
                                                base_experiment,
                                                replicate_1_1,
                                                replicate_2_1,
                                                library_1,
                                                library_2,
                                                biosample_1,
                                                mouse_donor_1_6,
                                                file_fastq_3,
                                                bigWig_file,
                                                file_bam_1_1,
                                                correlation_quality_metric,
                                                chip_seq_quality_metric,
                                                analysis_step_run_bam,
                                                analysis_step_version_bam,
                                                analysis_step_bam,
                                                pipeline_bam):
    testapp.patch_json(bigWig_file['@id'], {'dataset': base_experiment['@id']})
    testapp.patch_json(
        correlation_quality_metric['@id'], {'quality_metric_of': [bigWig_file['@id']],
                                            'Pearson correlation': 0.15})
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
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in collect_audit_errors(res))

# duplication rate audit was removed from v54


def test_audit_experiment_dnase_seq_missing_read_depth(testapp,
                                                       base_experiment,
                                                       replicate_1_1,
                                                       library_1,
                                                       biosample_1,
                                                       mouse_donor_1_6,
                                                       file_fastq_3,
                                                       file_bam_1_1,
                                                       mad_quality_metric_1_2,
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
               'missing read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_unfiltered_missing_read_depth(testapp,
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
                                                                 pipeline_bam,
                                                                 target_H3K9me3):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'unfiltered alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'unfiltered alignments',
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing read depth' for error in collect_audit_errors(res))


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


def test_audit_experiment_wgbs_standards(testapp,
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
                                         file_bed_methyl,
                                         wgbs_quality_metric,
                                         analysis_step_run_bam,
                                         analysis_step_version_bam,
                                         analysis_step_bam,
                                         pipeline_bam,
                                         target_H3K9me3):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'WGBS paired-end pipeline'})

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
                                                'assay_term_name': 'whole-genome shotgun bisulfite sequencing'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'high lambda C methylation ratio' for error in collect_audit_errors(res))


def test_audit_experiment_modern_chip_seq_standards(testapp,
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
                                                    analysis_step_run_bam,
                                                    analysis_step_version_bam,
                                                    analysis_step_bam,
                                                    pipeline_bam,
                                                    target,
                                                    award_modERN):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 100000,
                                                        'mapped': 100000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 100})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Transcription factor ChIP-seq pipeline (modERN)'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq',
                                                'award': award_modERN['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


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
    treatment_time_series,
    file_fastq_3,
    file_bam_1_1,
    file_tsv_1_2,
    analysis_step_run_bam,
    pipeline_bam,
    target_H3K9me3,
):
    testapp.patch_json(
        treatment_time_series['@id'],
        {'related_datasets': [experiment['@id']]}
    )
    testapp.patch_json(
        base_experiment['@id'],
        {
            'target': target_H3K9me3['@id'],
            'possible_controls': [treatment_time_series['@id']],
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
            'dataset': treatment_time_series['@id'],
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


def test_audit_experiment_control(testapp, base_matched_set, ChIP_experiment, experiment, base_experiment):
    ctrl = testapp.patch_json(base_matched_set['@id'], {'related_datasets': [experiment['@id'],
                                                                        base_experiment['@id']]})
    res = testapp.get(ChIP_experiment['@id'] + '@@index-data')
    assert (error['category'] == 'inconsistent control' for error in collect_audit_errors(res))
    ctrl = testapp.patch_json(base_matched_set['@id'], {'related_datasets': [experiment['@id']]})
    res = testapp.get(ChIP_experiment['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent control' for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_analyses_files(testapp, experiment_with_analyses, experiment_with_analyses_2, file_bam_1_1, file_bam_2_1, bigWig_file):
    testapp.patch_json(file_bam_1_1['@id'], {
        'dataset': experiment_with_analyses['@id'],
        })
    testapp.patch_json(file_bam_2_1['@id'], {
        'dataset': experiment_with_analyses['@id'],
        })
    res = testapp.get(experiment_with_analyses['@id'] + '@@index-data')
    assert not any(error['category'] == 'inconsistent analyses files' for error in collect_audit_errors(res))
    testapp.patch_json(bigWig_file['@id'], {
        'dataset': experiment_with_analyses['@id'],
        })
    res = testapp.get(experiment_with_analyses['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analyses files' for error in collect_audit_errors(res))
    testapp.patch_json(file_bam_1_1['@id'], {
        'dataset': experiment_with_analyses_2['@id'],
        })
    testapp.patch_json(file_bam_2_1['@id'], {
        'dataset': experiment_with_analyses_2['@id'],
        })
    res = testapp.get(experiment_with_analyses_2['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent analyses files' for error in collect_audit_errors(res))


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


def test_audit_experiment_ATAC_ENCODE4_QC_standards(
        testapp, ATAC_bam, ATAC_experiment, ATAC_pipeline,
        analysis_step_atac_encode4_alignment,
        atac_alignment_quality_metric_low,
        atac_library_complexity_quality_metric_poor,
        atac_align_enrich_quality_metric_med,
        atac_peak_enrichment_quality_metric_2, file_fastq_1_atac,
        analysis_step_atac_encode4_pseudoreplicate_concordance,
        file_bed_pseudo_replicated_peaks_atac, ATAC_experiment_replicated,
        file_bed_replicated_peaks_atac, replicate_ATAC_seq,
        atac_replication_quality_metric_borderline_replicate_concordance,
        library_1, biosample_human_1, library_2, biosample_human_2,
        atac_replication_quality_metric_high_peaks, file_bed_IDR_peaks_atac,
        atac_rep_metric_low_qual, file_bed_IDR_peaks_2_atac
        ):
    # https://encodedcc.atlassian.net/browse/ENCD-5255
    # https://encodedcc.atlassian.net/browse/ENCD-5350
    # https://encodedcc.atlassian.net/browse/ENCD-5468
    testapp.patch_json(atac_alignment_quality_metric_low['@id'],
                        {'quality_metric_of': [ATAC_bam['@id']]})
    testapp.patch_json(atac_library_complexity_quality_metric_poor['@id'],
                        {'quality_metric_of': [ATAC_bam['@id']]})
    testapp.patch_json(atac_align_enrich_quality_metric_med['@id'],
                        {'quality_metric_of': [ATAC_bam['@id']]})
    testapp.patch_json(
        atac_peak_enrichment_quality_metric_2['@id'],
        {'quality_metric_of': [file_bed_pseudo_replicated_peaks_atac['@id']]}
        )
    testapp.patch_json(atac_replication_quality_metric_borderline_replicate_concordance['@id'],
                       {'quality_metric_of': [file_bed_pseudo_replicated_peaks_atac['@id']]})
    res = testapp.get(ATAC_experiment['@id'] + '@@index-data')
    audit_errors = collect_audit_errors(res)
    assert any(error['category'] == 'low alignment rate' for error in audit_errors)
    assert any(error['category'] == 'poor library complexity' for error in audit_errors)
    assert any(error['category'] == 'mild to moderate bottlenecking' for error in audit_errors)
    assert any(error['category'] == 'severe bottlenecking' for error in audit_errors)
    assert any(error['category'] == 'moderate TSS enrichment' for error in audit_errors)
    assert any(error['category'] == 'extremely low read depth' for error in audit_errors)
    assert any(error['category'] == 'no peaks in nucleosome-free regions' for error in audit_errors)
    assert any(error['category'] == 'low FRiP score' for error in audit_errors)
    assert any(error['category'] == 'negative RSC' for error in audit_errors)
    assert any(error['category'] == 'negative NSC' for error in audit_errors)
    assert 'borderline replicate concordance' not in (error['category'] for error in collect_audit_errors(res))

    testapp.patch_json(atac_replication_quality_metric_borderline_replicate_concordance['@id'],
                       {'quality_metric_of': [file_bed_replicated_peaks_atac['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_human_1['uuid']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_human_2['uuid']})
    testapp.patch_json(replicate_ATAC_seq['@id'], {'experiment': ATAC_experiment_replicated['@id']})
    testapp.patch_json(file_fastq_1_atac['@id'], {'dataset': ATAC_experiment_replicated['@id']})
    res2 = testapp.get(ATAC_experiment_replicated['@id'] + '@@index-data')
    assert any(error['category'] == 'borderline replicate concordance' for error in collect_audit_errors(res2))
    assert any(error['category'] == 'insufficient number of reproducible peaks' for error in collect_audit_errors(res2))

    # When reproducible peaks are checked in multiple files, the better value is reported
    testapp.patch_json(atac_replication_quality_metric_high_peaks['@id'],
                       {'quality_metric_of': [file_bed_IDR_peaks_atac['@id']]})
    res2 = testapp.get(ATAC_experiment_replicated['@id'] + '@@index-data')
    assert 'insufficient number of reproducible peaks' not in (error['category'] for error in collect_audit_errors(res2))

    # Reproducible peaks are checked for each pairwise comparison of replicates
    testapp.patch_json(atac_rep_metric_low_qual['@id'],
                       {'quality_metric_of': [file_bed_IDR_peaks_2_atac['@id']]})
    res2 = testapp.get(ATAC_experiment_replicated['@id'] + '@@index-data')
    assert any(error['category'] == 'insufficient number of reproducible peaks' and \
               'replicate(s) [2, 3]' in error['detail'] for error in collect_audit_errors(res2))

    # Multiple AtacReplicationQualityMetric objects on the same file is flagged
    testapp.patch_json(atac_replication_quality_metric_high_peaks['@id'],
                       {'quality_metric_of': [file_bed_IDR_peaks_2_atac['@id']]})
    res2 = testapp.get(ATAC_experiment_replicated['@id'] + '@@index-data')
    assert any(error['category'] == 'duplicate QC metrics' for error in collect_audit_errors(res2))


def test_audit_experiment_analysis_files(
    testapp,
    base_experiment,
    ctrl_experiment,
    base_analysis,
    file1,
    file2
):
    testapp.patch_json(file1['@id'], {'dataset': ctrl_experiment['@id']})
    testapp.patch_json(file2['@id'], {'dataset': ctrl_experiment['@id']})
    testapp.patch_json(base_analysis['@id'], {'files': [file1['@id']]})
    testapp.patch_json(
        base_experiment['@id'], {'analysis_objects': [base_analysis['@id']]}
    )
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'inconsistent analysis files'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(file1['@id'], {'dataset': base_experiment['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(
        error['category'] != 'inconsistent analysis files'
        for error in collect_audit_errors(res)
    )
    testapp.patch_json(
        base_analysis['@id'], {'files': [file1['@id'], file2['@id']]}
    )
    testapp.patch_json(file1['@id'], {'derived_from': [file2['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'inconsistent analysis files'
        for error in collect_audit_errors(res)
    )
