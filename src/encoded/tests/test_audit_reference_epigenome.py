import pytest


def test_reference_epigenome_without_required_assays(testapp, reference_epigenome_1):
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'partial reference epigenome' for error in errors_list)


def test_reference_epigenome_with_required_assays(testapp, reference_epigenome_1,
                                                  reference_experiment_RNA_seq,
                                                  reference_experiment_RRBS,
                                                  reference_experiment_WGBS,
                                                  reference_experiment_chip_seq_control,
                                                  reference_experiment_chip_seq_H3K27me3,
                                                  reference_experiment_chip_seq_H3K36me3,
                                                  reference_experiment_chip_seq_H3K4me1,
                                                  reference_experiment_chip_seq_H3K4me3,
                                                  reference_experiment_chip_seq_H3K27ac,
                                                  reference_experiment_chip_seq_H3K9me3,
                                                  ):
    testapp.patch_json(reference_epigenome_1['@id'], {'related_datasets':
                                                      [reference_experiment_RNA_seq['@id'],
                                                       reference_experiment_RRBS['@id'],
                                                       reference_experiment_WGBS['@id'],
                                                       reference_experiment_chip_seq_control['@id'],
                                                       reference_experiment_chip_seq_H3K27me3[
                                                       '@id'],
                                                       reference_experiment_chip_seq_H3K36me3[
                                                       '@id'],
                                                       reference_experiment_chip_seq_H3K4me1['@id'],
                                                       reference_experiment_chip_seq_H3K4me3['@id'],
                                                       reference_experiment_chip_seq_H3K27ac['@id'],
                                                       reference_experiment_chip_seq_H3K9me3['@id']
                                                       ]})
    testapp.patch_json(reference_experiment_RNA_seq['@id'], {'status': 'in progress'})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'partial reference epigenome' for error in errors_list)
    testapp.patch_json(reference_experiment_RNA_seq['@id'], {'status': 'released'})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'partial reference epigenome' for error in errors_list)


def test_reference_epigenome_multiple_biosample_term_names(testapp, reference_epigenome_1,
                                                           reference_experiment_RNA_seq,
                                                           reference_experiment_RRBS,
                                                           replicate_RNA_seq,
                                                           replicate_RRBS,
                                                           library_1,
                                                           library_2,
                                                           biosample_1,
                                                           biosample_2,
                                                           donor_1,
                                                           donor_2,
                                                           liver,
                                                           heart):
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            'biosample_ontology': liver['uuid']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            'biosample_ontology': heart['uuid']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(reference_epigenome_1['@id'], {'related_datasets':
                                                      [reference_experiment_RNA_seq['@id'],
                                                       reference_experiment_RRBS['@id']]})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'multiple biosample term names in reference epigenome' for
               error in errors_list)


def test_reference_epigenome_multiple_biosample_treatments(testapp, reference_epigenome_1,
                                                           reference_experiment_RNA_seq,
                                                           reference_experiment_RRBS,
                                                           replicate_RNA_seq,
                                                           replicate_RRBS,
                                                           treatment_5,
                                                           library_1,
                                                           library_2,
                                                           biosample_1,
                                                           biosample_2):
    testapp.patch_json(biosample_1['@id'], {'treatments': [treatment_5['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(reference_epigenome_1['@id'], {'related_datasets':
                                                      [reference_experiment_RNA_seq['@id'],
                                                       reference_experiment_RRBS['@id']]})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'multiple biosample treatments in reference epigenome' for
               error in errors_list)
