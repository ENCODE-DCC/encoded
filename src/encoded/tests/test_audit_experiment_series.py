import pytest


def test_experiment_series_mismatched_assays(testapp,
                                             experiment_series_1,
                                             experiment_rna,
                                             experiment_dnase,
                                             experiment_chip_CTCF
                                            ):
  testapp.patch_json(experiment_series_1['@id'], {'related_datasets':
                                                    [experiment_dnase['@id'],
                                                     experiment_rna['@id'],
                                                     experiment_chip_CTCF['@id']]})
  testapp.patch_json(experiment_series_1['@id'], {'aliases': ['encode:test_alias_02']})
  res = testapp.get(experiment_series_1['@id'] + '@@index-data')
  errors = res.json['audit']
  errors_list = []
  for error_type in errors:
      errors_list.extend(errors[error_type])
  assert any(error['category'] == 'Mismatched assays' for
             error in errors_list)


def test_experiment_series_mismatched_biosamples(testapp,
                                                 experiment_series_1,
                                                 experiment_rna,
                                                 experiment_dnase,
                                                 library_1,
                                                 library_2,
                                                 biosample_1,
                                                 biosample_2,
                                                 ileum
                                                ):
  testapp.patch_json(biosample_1['@id'], {'biosample_ontology': ileum['uuid']})
  testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
  testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
  testapp.patch_json(experiment_series_1['@id'], {'related_datasets':
                                                    [experiment_dnase['@id'],
                                                     experiment_rna['@id']]})
  res = testapp.get(experiment_series_1['@id'] + '@@index-data')
  errors = res.json['audit']
  errors_list = []
  for error_type in errors:
      errors_list.extend(errors[error_type])
  assert any(error['category'] == 'Mismatched biosamples' for
             error in errors_list)


def test_experiment_series_mismatched_targets(testapp,
                                              experiment_series_1,
                                              experiment_chip_CTCF,
                                              experiment_chip_H3K4me3,
                                              ):
  testapp.patch_json(experiment_series_1['@id'], {'related_datasets':
                                                      [experiment_chip_CTCF['@id'],
                                                       experiment_chip_H3K4me3['@id']]})
  res = testapp.get(experiment_series_1['@id'] + '@@index-data')
  errors = res.json['audit']
  errors_list = []
  for error_type in errors:
    errors_list.extend(errors[error_type])
  assert any(error['category'] == 'Mismatched targets' for
               error in errors_list)


def test_experiment_series_mismatched_donors(testapp,
                                             experiment_series_1,
                                             experiment_rna,
                                             experiment_dnase,
                                             library_1,
                                             library_2,
                                             replicate_dnase,
                                             replicate_rna,
                                             biosample_1,
                                             biosample_2,
                                             donor_1,
                                             donor_2
                                             ):
  testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
  testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})
  testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
  testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
  testapp.patch_json(experiment_series_1['@id'], {'related_datasets':
                                                    [experiment_dnase['@id'],
                                                     experiment_rna['@id']]})
  res = testapp.get(experiment_series_1['@id'] + '@@index-data')
  errors = res.json['audit']
  errors_list = []
  for error_type in errors:
      errors_list.extend(errors[error_type])
  assert any(error['category'] == 'Mismatched donors' for
             error in errors_list)


def test_experiment_series_mismatched_treatments(testapp,
                                                 experiment_series_1,
                                                 experiment_rna,
                                                 experiment_dnase,
                                                 treatment_5,
                                                 library_1,
                                                 library_2,
                                                 replicate_dnase,
                                                 replicate_rna,
                                                 biosample_1,
                                                 biosample_2
                                                 ):
  testapp.patch_json(biosample_1['@id'], {'treatments': [treatment_5['@id']]})
  testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
  testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
  testapp.patch_json(experiment_series_1['@id'], {'related_datasets':
                                                    [experiment_dnase['@id'],
                                                     experiment_rna['@id']]})
  res = testapp.get(experiment_series_1['@id'] + '@@index-data')
  errors = res.json['audit']
  errors_list = []
  for error_type in errors:
      errors_list.extend(errors[error_type])
  assert any(error['category'] == 'Mismatched biosample treatments' for
             error in errors_list)


def test_experiment_series_mismatched_genetic_modifications(testapp,
                                                            experiment_series_1,
                                                            experiment_rna,
                                                            experiment_dnase,
                                                            construct_genetic_modification,
                                                            library_1,
                                                            library_2,
                                                            replicate_dnase,
                                                            replicate_rna,
                                                            biosample_1,
                                                            biosample_2
                                                            ):
  testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [construct_genetic_modification['@id']]})
  testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
  testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
  testapp.patch_json(experiment_series_1['@id'], {'related_datasets':
                                                    [experiment_dnase['@id'],
                                                     experiment_rna['@id']]})
  res = testapp.get(experiment_series_1['@id'] + '@@index-data')
  errors = res.json['audit']
  errors_list = []
  for error_type in errors:
      errors_list.extend(errors[error_type])
  assert any(error['category'] == 'Mismatched genetic modifications' for
             error in errors_list)
