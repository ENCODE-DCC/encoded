import pytest
from ..constants import *


@pytest.fixture
def biosample_characterization(testapp, award, lab, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]



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
def functional_characterization_experiment_4(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'status': 'in progress',
        'target_expression_percentile': 70
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
def biosample_characterization_base(submitter, award, lab, biosample):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': biosample['uuid'],
    }


@pytest.fixture
def antibody_characterization_1(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '1',
        'status': 'SUBMITTED',
        'characterization_method': 'mass spectrometry after IP',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT}
    })
    return item


@pytest.fixture
def antibody_characterization_2(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '3',
        'status': 'COMPLIANT'
    })
    return item


@pytest.fixture
def biosample_characterization_1(biosample_characterization_base):
    item = biosample_characterization_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'APPROVED',
        'characterization_method': 'immunofluorescence',
    })
    return item


@pytest.fixture
def biosample_characterization_2(biosample_characterization_base):
    item = biosample_characterization_base.copy()
    item.update({
        'schema_version': '3',
        'status': 'IN PROGRESS',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def antibody_characterization_3(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '4',
        'characterization_method': 'immunoblot',
    })
    return item


@pytest.fixture
def biosample_characterization_4(root, biosample_characterization, publication):
    item = root.get_by_uuid(biosample_characterization['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '4',
        'references': [publication['identifiers'][0]],
    })
    return properties


@pytest.fixture
def antibody_characterization_10(antibody_characterization_1):
    item = antibody_characterization_1.copy()
    item.update({
        'status': 'pending dcc review',
        'characterization_method': 'immunoprecipitation followed by mass spectrometry',
        'comment': 'We tried really hard to characterize this antibody.',
        'notes': 'Your plea has been noted.'
    })
    return item


@pytest.fixture
def antibody_characterization_11(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'characterization_reviews': [{
            'biosample_term_name': 'K562',
            'biosample_term_id': 'EFO:0002067',
            'lane_status': 'exempt from standards',
            'biosample_type': 'immortalized cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }]
    })
    return item


@pytest.fixture
def antibody_characterization_13(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'characterization_reviews': [{
            'biosample_term_name': 'HUES62',
            'biosample_term_id': 'EFO:0007087',
            'lane_status': 'exempt from standards',
            'biosample_type': 'induced pluripotent stem cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }]
    })
    return item


@pytest.fixture
def antibody_characterization_14(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'characterization_reviews': [{
            'biosample_term_name': 'A549',
            'biosample_term_id': 'EFO:0001086',
            'lane_status': 'exempt from standards',
            'biosample_type': 'cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }]
    })
    return item

