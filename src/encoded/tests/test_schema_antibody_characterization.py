import pytest

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid']
    }


def test_antibody_characterization_reviews(testapp, antibody_characterization, k562):
    antibody_characterization['characterization_reviews'] = [{
        "organism": "human",
        "lane": 2,
        "biosample_ontology": k562['uuid'],
    }]
    testapp.post_json('/antibody_characterization', antibody_characterization, status=422)


def test_antibody_characterizaton_two_methods(testapp, antibody_characterization):
    antibody_characterization['primary_characterization_method'] = 'immunoblot'
    antibody_characterization['secondary_characterization_method'] = 'dot blot assay'
    antibody_characterization['attachment'] = {'download': 'red-dot.png', 'href': RED_DOT}
    testapp.post_json('/antibody_characterization', antibody_characterization, status=422)


def test_antibody_status_wrangler(testapp, antibody_characterization):
    antibody_characterization['primary_characterization_method'] = 'immunoblot'
    antibody_characterization['status'] = 'compliant'
    testapp.post_json('/antibody_characterization', antibody_characterization, status=422)


def test_no_attachment(testapp, antibody_characterization):
    antibody_characterization['secondary_characterization_method'] = 'ChIP-seq comparison'
    testapp.post_json('/antibody_characterization', antibody_characterization, status=422)


def test_antibody_characterization_exemption_no_explanation(testapp,
                                                            antibody_characterization,
                                                            document,
                                                            k562):
    antibody_characterization['characterization_reviews'] = [{"organism": "human", "lane": 2,
                                                              "biosample_ontology": k562['uuid'],
                                                              "lane_status":
                                                              "exempt from standards"}]
    antibody_characterization['documents'] = [document]
    antibody_characterization['reviewed_by'] = '81a6cc12-2847-4e2e-8f2c-f566699eb29e'
    testapp.post_json('/antibody_characterization', antibody_characterization, status=422)
