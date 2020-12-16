import pytest


@pytest.fixture
def functional_characterization_experiment_item(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'STARR-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return item


@pytest.fixture
def functional_characterization_experiment_screen(testapp, lab, award, heart, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress',
        'target': target['uuid']

    }
    return item


@pytest.fixture
def functional_characterization_experiment(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'STARR-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/functional_characterization_experiment', item).json['@graph'][0]


@pytest.fixture
def functional_characterization_experiment_4(testapp, lab, award, heart):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'status': 'in progress',
        'target_expression_percentile': 70,
        'biosample_ontology': heart['uuid']
    }
    return item


@pytest.fixture
def functional_characterization_experiment_5(testapp, lab, award, ctcf):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'status': 'in progress',
        'examined_loci': [{
             'gene': ctcf['uuid'],
             'gene_expression_percentile': 80
         }]
    }
    return item
    

@pytest.fixture
def functional_characterization_experiment_6(testapp, lab, award, ctcf, heart):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress',
        'examined_loci': [{
             'gene': ctcf['uuid']
         }]
    }
    return item


@pytest.fixture
def base_fcc_experiment(testapp, lab, award, heart):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'MPRA',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/functional-characterization-experiments', item, status=201).json['@graph'][0]


@pytest.fixture
def functional_characterization_experiment_disruption_screen(testapp, lab, award, liver):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'biosample_ontology': liver['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/functional_characterization_experiment', item).json['@graph'][0]


@pytest.fixture
def pce_fcc_experiment(testapp, lab, award):
        return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'pooled clone sequencing',
        'schema_version': '2',
        'status': 'in progress'
    }


@pytest.fixture
def pce_fcc_experiment_2(pce_fcc_experiment):
    item = pce_fcc_experiment.copy()
    item.update({
        'schema_version': '4'
    })
    return item


@pytest.fixture
def pce_fcc_other_experiment(pce_fcc_experiment):
    item = pce_fcc_experiment.copy()
    item.update({
        'schema_version': '5',
        'plasmids_library_type': 'other'
    })
    return item


@pytest.fixture
def pooled_clone_sequencing(testapp, lab, award, liver):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'pooled clone sequencing',
        'biosample_ontology': liver['uuid'],
        'plasmids_library_type': 'elements cloning'
    }
    return testapp.post_json(
        '/functional_characterization_experiment', item
    ).json['@graph'][0]
