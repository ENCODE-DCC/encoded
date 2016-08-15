import pytest


@pytest.fixture
def human_donor(testapp, award, lab, human):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': human['@id'],
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


def test_undefined_sex_model_organism(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'unknown'


def test_undefined_sex_human(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'unknown'


def test_undefined_sex_mouse_with_model_organism_sex_field(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_sex': 'female'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'female'


def test_undefined_sex_human_with_model_organism_sex_field(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_sex': 'female'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'unknown'


def test_defined_human_sex_with_conflicting_model_organism_sex_field(testapp, biosample, human,
                                                                     human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_sex': 'female'})
    testapp.patch_json(human_donor['@id'], {'sex': 'male'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['sex'] == 'male'


def test_undefined_age_model_organism(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == 'unknown'


def test_undefined_age_human(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == 'unknown'


def test_undefined_age_mouse_with_model_organism_age_field(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_age': '120'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == '120'


def test_undefined_age_human_with_model_organism_age_field(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_age': '125'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == 'unknown'


def test_defined_human_age_with_conflicting_model_organism_age_field(testapp, biosample, human,
                                                                     human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_age': '125'})
    testapp.patch_json(human_donor['@id'], {'age': '14', 'age_units': 'year'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age'] == '14'


def test_undefined_age_units_model_organism(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'age_units' not in res.json['object']


def test_undefined_age_units_human(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'age_units' not in res.json['object']


def test_undefined_age_units_mouse_with_model_organism_age_field(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_age': '120'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'age_units' not in res.json['object']


def test_undefined_age_units_human_with_model_organism_age_field(testapp, biosample, human):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_age': '125'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'age_units' not in res.json['object']


def test_defined_human_age_units_with_conflicting_model_organism_age_field(testapp, biosample,
                                                                           human, human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_age': '125',
                                          'model_organism_age_units': 'week'})
    testapp.patch_json(human_donor['@id'], {'age': '14', 'age_units': 'year'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['age_units'] == 'year'


def test_defined_life_stage_human(testapp, biosample, human, human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(human_donor['@id'], {'life_stage': 'fetal'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'fetal'


def test_undefined_life_stage_human(testapp, biosample, human, human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'unknown'


def test_defined_life_stage_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'mouse_life_stage': 'adult'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'adult'


def test_undefined_life_stage_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['life_stage'] == 'unknown'


def test_defined_health_status_human(testapp, biosample, human, human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(human_donor['@id'], {'health_status': 'healthy'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['health_status'] == 'healthy'


def test_undefined_health_status_human(testapp, biosample, human, human_donor):
    testapp.patch_json(biosample['@id'], {'organism': human['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_health_status': 'healthy'})
    testapp.patch_json(biosample['@id'], {'donor': human_donor['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'health_status' not in res.json['object']


def test_defined_health_status_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(biosample['@id'], {'model_organism_health_status': 'sick'})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert res.json['object']['health_status'] == 'sick'


def test_undefined_health_status_mouse(testapp, biosample, mouse):
    testapp.patch_json(biosample['@id'], {'organism': mouse['@id']})
    res = testapp.get(biosample['@id'] + '@@index-data')
    assert 'health_status' not in res.json['object']

'''
def test_biosample_summary(testapp,
                           donor_1,
                           biosample_1, treatment):
    testapp.patch_json(donor_1['@id'], {'age_units': 'day', 'age': '10'})
    testapp.patch_json(donor_1['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            "biosample_term_id": "EFO:0002784",
                                            "biosample_term_name": "liver",
                                            "biosample_type": "tissue",
                                            'treatments': [treatment['@id']]})
    res = testapp.get(biosample_1['@id']+'@@index-data')
    assert res.json['object']['summary'] == \
        'Homo sapiens liver tissue male (10 days) treated with ethanol'

'''
def test_biosample_summary_construct(testapp,
                                     fly,
                                     fly_donor,
                                     biosample_1,
                                     construct):
    print (construct)
    print (biosample_1)
    #testapp.patch_json(fly_donor['@id'], {'age_units': 'day', 'age': '10'})
    #testapp.patch_json(fly_donor['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': fly_donor['@id'],
                                            'biosample_term_id': 'EFO:0002784',
                                            'biosample_term_name': 'liver',
                                            'biosample_type': 'tissue',
                                            'constructs': [construct['@id']],
                                            'model_organism_age': '10',
                                            'model_organism_age_units': 'day',
                                            'model_organism_sex': 'female',
                                            'organism': fly['@id']})

    res = testapp.get(biosample_1['@id']+'@@index-data')
    print (biosample_1)
    print (res.json['object']['summary'])
    assert res.json['object']['summary'] == \
        'Homo sapiens liver tissue male (10 days) expressing ATF4'
