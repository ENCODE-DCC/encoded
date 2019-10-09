import pytest


@pytest.fixture
def experiment_series_1(testapp, lab, award, base_experiment):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'related_datasets': [base_experiment['@id']]
    }
    return testapp.post_json('/experiment_series', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_chip_H3K4me3(testapp, lab, award, target_H3K4me3, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_chip_CTCF(testapp, lab, award, target_CTCF, k562):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': k562['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_CTCF['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_rna(testapp, lab, award, h1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': h1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_dnase(testapp, lab, award, heart):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'assay_term_name': 'DNase-seq',
        'biosample_ontology': heart['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def target_H3K4me3(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_CTCF(testapp, organism):
    item = {
        'label': 'CTCF',
        'target_organism': organism['@id'],
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def replicate_dnase(testapp, experiment_dnase, library_1):
    item = {
        'experiment': experiment_dnase['@id'],
        'library': library_1['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_rna(testapp, experiment_rna, library_2):
    item = {
        'experiment': experiment_rna['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


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
                                                 treatment,
                                                 library_1,
                                                 library_2,
                                                 replicate_dnase,
                                                 replicate_rna,
                                                 biosample_1,
                                                 biosample_2
                                                 ):
  testapp.patch_json(biosample_1['@id'], {'treatments': [treatment['@id']]})
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
