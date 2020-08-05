import pytest


@pytest.fixture
def encode4_tag_antibody_lot(testapp, lab, encode4_award, mouse, gfp_target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'source': 'Acme',
        'host_organism': mouse['@id'],
        'targets': [gfp_target['@id']],
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


@pytest.fixture
def antibody_lot_base(lab, award):
    return {
        'product_id': 'SAB2100398',
        'lot_id': 'QC8343',
        'source': 'Acme',
    }


@pytest.fixture
def antibody_lot_1(antibody_lot_base):
    item = antibody_lot_base.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['CEBPZ'],
    })
    return item


@pytest.fixture
def antibody_lot_2(antibody_lot_base):
    item = antibody_lot_base.copy()
    item.update({
        'schema_version': '2',
        'status': "CURRENT"
    })
    return item


@pytest.fixture
def antibody_lot_3(root, antibody_lot):
    item = root.get_by_uuid(antibody_lot['uuid'])
    properties = item.properties.copy()
    del properties['targets']
    properties.update({
        'schema_version': '3'
    })
    return properties


@pytest.fixture
def antibody_lot_4(root, antibody_lot_3):
    item = antibody_lot_3.copy()
    item.update({
        'schema_version': '4',
        'lot_id_alias': ['testing:456', 'testing:456'],
        'purifications': ['crude', 'crude']
    })
    return item


@pytest.fixture
def mass_spec(testapp, award, lab, antibody_lot, target, attachment):
    item = {
        'lab': lab['@id'],
        'target': target['@id'],
        'characterizes': antibody_lot['@id'],
        'attachment': attachment,
        'secondary_characterization_method': 'immunoprecipitation followed by mass spectrometry',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def antibody_lot(testapp, lab, award, mouse, target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'source': 'Acme',
        'host_organism': mouse['@id'],
        'targets': [target['@id']],
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


@pytest.fixture
def immunoblot(testapp, award, lab, antibody_lot, target, attachment):
    item = {
        'target': target['@id'],
        'characterizes': antibody_lot['@id'],
        'attachment': attachment,
        'primary_characterization_method': 'immunoblot',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def immunoprecipitation(immunoblot):
    item = immunoblot.copy()
    item.update({'primary_characterization_method': 'immunoprecipitation'})
    return item


@pytest.fixture
def motif_enrichment(mass_spec):
    item = mass_spec.copy()
    item.update({'secondary_characterization_method': 'motif enrichment'})
    return item
