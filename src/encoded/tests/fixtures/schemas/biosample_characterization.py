import pytest


@pytest.fixture
def biosample_characterization_no_review(testapp, award, lab, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


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
def biosample_characterization_2nd_opinion(testapp, award, lab, submitter, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'status': 'requires secondary opinion',
            'lab': lab['@id'],
            'reviewed_by': submitter['@id'],
        },
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


@pytest.fixture
def biosample_characterization_exempt(testapp, award, lab, submitter, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'status': 'exempt from standards',
            'lab': lab['@id'],
            'reviewed_by': submitter['@id'],
        },
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


@pytest.fixture
def biosample_characterization_not_compliant(testapp, award, lab, submitter, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'status': 'not compliant',
            'lab': lab['@id'],
            'reviewed_by': submitter['@id'],
        },
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


@pytest.fixture
def biosample_characterization_compliant(testapp, award, lab, submitter, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'status': 'compliant',
            'lab': lab['@id'],
            'reviewed_by': submitter['@id'],
        },
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


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
