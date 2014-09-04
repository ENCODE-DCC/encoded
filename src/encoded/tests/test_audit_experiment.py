import pytest


@pytest.fixture
def base_experiment(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def base_biosample(testapp, lab, award, source, organism):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_library(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'gene_name': 'XYZ',
        'label': 'XYZ',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def tag_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'eGFP',
        'investigated_as': ['tag']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def histone_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'Histone',
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody(award, lab, source, organism, target):
   return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [target['uuid']],
        'product_id': 'KDKF123',
        'lot_id': '123'
    }


@pytest.fixture
def base_antibody_characterization1(testapp, lab, award, target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'characterization_reviews': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_term_name': 'K562',
                'biosample_term_id': 'EFO:0002067',
                'biosample_type': 'immortalized cell line',
                'lane_status': 'compliant'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay'
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


def test_audit_experiment_target(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing target' for error in errors)


def test_audit_experiment_replicate_paired_end(testapp, base_experiment, base_replicate):
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing replicate paired end' for error in errors)


def test_audit_experiment_library_paired_end(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'missing library paired end' for error in errors)


def test_audit_experiment_paired_end_mismatch(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_library['@id'], {'paired_ended': False })
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id'], 'paired_ended': True})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'paired end mismatch' for error in errors)


def test_audit_experiment_paired_end_required(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0001849', 'assay_term_name': 'DNA-PET'})
    testapp.patch_json(base_library['@id'], {'paired_ended': False })
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id'], 'paired_ended': True})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'paired end required for assay' for error in errors)


def test_audit_experiment_not_tag_antibody(testapp, base_experiment, base_replicate, organism, antibody_lot):
    other_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'eGFP-AVCD', 'investigated_as': ['recombinant protein']}).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': other_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'not tagged antibody' for error in errors)


def test_audit_experiment_target_tag_antibody(testapp, base_experiment, base_replicate, organism, base_antibody, tag_target):
    ha_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'HA-ABCD', 'investigated_as': ['recombinant protein']}).json['@graph'][0]
    base_antibody['targets'] = [tag_target['@id']]
    tag_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': tag_antibody['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': ha_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'tag target mismatch' for error in errors)


def test_audit_experiment_target_mismatch(testapp, base_experiment, base_replicate, base_target, antibody_lot):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'target mismatch' for error in errors)


def test_audit_experiment_eligible_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, antibody_lot, target, base_antibody_characterization1, base_antibody_characterization2):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'], 'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'biosample_term_id': 'EFO:0002067', 'biosample_term_name': 'K562',  'biosample_type': 'immortalized cell line', 'target': 
    target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'not eligible antibody' for error in errors)


def test_audit_experiment_eligible_histone_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, base_antibody, histone_target, base_antibody_characterization1, base_antibody_characterization2):
    base_antibody['targets'] = [histone_target['@id']]
    histone_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_antibody_characterization1['@id'], {'target': histone_target['@id'], 'characterizes': histone_antibody['@id']})
    testapp.patch_json(base_antibody_characterization2['@id'], {'target': histone_target['@id'], 'characterizes': histone_antibody['@id']})
    testapp.patch_json(base_replicate['@id'], {'antibody': histone_antibody['@id'], 'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'biosample_term_id': 'EFO:0002067', 'biosample_term_name': 'K562',  'biosample_type': 'immortalized cell line', 'target': 
    histone_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'not eligible histone antibody' for error in errors)


def test_audit_experiment_biosample_type_missing(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': "EFO:0002067", 'biosample_term_name':'K562'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'biosample type missing' for error in errors)
