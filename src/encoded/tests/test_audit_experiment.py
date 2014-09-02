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
def base_library(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
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
def base_antibody_characterization1(testapp, lab, award, base_target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': base_target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'status': 'not compliant',
        'characterization_reviews': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_term_name': 'K562',
                'biosample_term_id': 'EFO:0002067',
                'biosample_type': 'immortalized cell line',
                'lane_status': 'not compliant'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, base_target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': base_target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay',
        'status': 'compliant'
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


def test_audit_experiment_target_mistmatch(testapp, base_experiment, base_replicate, organism, antibody_lot):
    other_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'ABC', 'investigated_as': ['transcription factor']}).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': other_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'target mismatch' for error in errors)


def test_audit_experiment_not_tag_antibody(testapp, base_experiment, base_replicate, organism, antibody_lot):
    other_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'eGFP', 'investigated_as': ['tag']}).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': other_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'not tagged antibody' for error in errors)


def test_audit_experiment_target_tag_antibody(testapp, base_experiment, base_replicate, organism, antibody_lot, base_target):
    ha_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'HA', 'investigated_as': ['tag']}).json['@graph'][0]
    testapp.patch_json(antibody_lot['@id'], {'targets': [ha_target['@id']]})
    testapp.patch_json(base_target['@id'], {'investigated_as': ['tag']})
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'tag target mismatch' for error in errors)

# These don't work right now
#def test_audit_experiment_eligible_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, antibody_lot, base_antibody_characterization1, base_antibody_characterization2, base_target):
#    testapp.patch_json(antibody_lot['@id'], {'targets': [base_target['@id']]})
#    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
#    testapp.patch_json(base_library['@id'], {'biosample': base_biosample['@id']})
#    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'], 'library': base_library['@id']})
#    res = testapp.get(base_experiment['@id'] + '@@index-data')
#    errors = res.json['audit']
#    assert any(error['category'] == 'not eligible antibody' for error in errors)


#def test_audit_experiment_eligible_antibody_histone(testapp, base_experiment, base_replicate, base_library, base_biosample, antibody_lot, base_antibody_characterization1, base_antibody_characterization2, base_target):
#    testapp.patch_json(base_target['@id'], {'investigated_as': ['histone modification']})
#    testapp.patch_json(antibody_lot['@id'], {'targets': [base_target['@id']]})
#    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
#    testapp.patch_json(base_library['@id'], {'biosample': base_biosample['@id']})
#    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'], 'library': base_library['@id']})
#    res = testapp.get(base_experiment['@id'] + '@@index-data')
#    errors = res.json['audit']
#    assert any(error['category'] == 'not eligible antibody' for error in errors)
