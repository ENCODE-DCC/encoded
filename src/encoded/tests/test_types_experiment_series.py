import pytest


@pytest.fixture
def experiment_1(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_2(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def base_experiment_series(testapp, lab, award, experiment_1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [experiment_1['@id']]
    }
    return testapp.post_json('/experiment-series', item, status=201).json['@graph'][0]


def test_experiment_series_biosample_summary(
    testapp,
    base_experiment_series,
    experiment_1,
    experiment_2,
    donor_1,
    donor_2,
    biosample_1,
    biosample_2,
    library_1,
    library_2,
    treatment,
    replicate_1_1,
    replicate_2_1,
    s2r_plus,
    liver
):
    testapp.patch_json(
        donor_1['@id'],
        {
            'age_units': 'year',
            'age': '55',
            'life_stage': 'embryonic',
            'sex': 'female'
        }
    )
    testapp.patch_json(
        donor_2['@id'],
        {'age_units': 'day', 'age': '1', 'life_stage': 'child', 'sex': 'male'}
    )
    testapp.patch_json(
        biosample_1['@id'],
        {
            'donor': donor_1['@id'],
            'treatments': [treatment['@id']],
            'biosample_ontology': s2r_plus['uuid'],
            'subcellular_fraction_term_name': 'nucleus',
        }
    )
    testapp.patch_json(
        biosample_2['@id'],
        {
            'donor': donor_2['@id'],
            'biosample_ontology': liver['uuid'],
            'treatments': [treatment['@id']]
        }
    )
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(
        replicate_1_1['@id'],
        {'library': library_1['@id'], 'experiment': experiment_1['@id']}
    )
    testapp.patch_json(
        replicate_2_1['@id'],
        {'library': library_2['@id'], 'experiment': experiment_2['@id']}
    )
    res = testapp.get(base_experiment_series['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == [
        'S2R+ nuclear fraction treated with ethanol'
    ]
    testapp.patch_json(
        base_experiment_series['@id'],
        {'related_datasets': [experiment_1['@id'], experiment_2['@id']]}
    )
    res = testapp.get(base_experiment_series['@id']+'@@index-data')
    assert sorted(res.json['object']['biosample_summary']) == [
        'S2R+ nuclear fraction treated with ethanol',
        'liver male child (1 day) treated with ethanol',
    ]
