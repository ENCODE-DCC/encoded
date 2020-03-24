import pytest


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
def base_replicate(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_rna(testapp, experiment_rna, library_2):
    item = {
        'experiment': experiment_rna['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]

@pytest.fixture
def base_replicate_two(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate_2(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def IgG_ctrl_rep(testapp, ctrl_experiment, IgG_antibody):
    item = {
        'experiment': ctrl_experiment['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'antibody': IgG_antibody['@id'],
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def replicate_1_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_2_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 2,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_1_2(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

@pytest.fixture
def file_rep(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]




@pytest.fixture
def file_rep2(replicate, file_exp2, testapp):
    item = {
        'experiment': file_exp2['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file_rep1_2(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 2,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_RNA_seq(testapp, reference_experiment_RNA_seq, library_1):
    item = {
        'experiment': reference_experiment_RNA_seq['@id'],
        'library': library_1['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_RRBS(testapp, reference_experiment_RRBS, library_2):
    item = {
        'experiment': reference_experiment_RRBS['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]

@pytest.fixture
def rep1(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def rep2(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate(experiment):
    return {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }


@pytest.fixture
def replicate_url(testapp, experiment, library):
    import pdb; pdb.set_trace();
    item = {
        'experiment': experiment['@id'],
        'library': library['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_url(testapp, experiment, library_url):
    item = {
        'experiment': experiment['@id'],
        'library': library_url['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]



@pytest.fixture
def replicate_rbns(replicate):
    item = replicate.copy()
    item.update({
        'rbns_protein_concentration': 10,
        'rbns_protein_concentration_units': 'nM',
    })
    return item


@pytest.fixture
def replicate_rbns_no_units(replicate):
    item = replicate.copy()
    item.update({
        'rbns_protein_concentration': 10,
    })
    return item


@pytest.fixture
def replicate_4(root, replicate_url, library_url):
    item = root.get_by_uuid(replicate_url['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '1',
        'library': library_url['uuid'],
        'paired_ended': False
    })
    return properties


@pytest.fixture
def replicate_3(root, replicate_url):
    item = root.get_by_uuid(replicate_url['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'notes': 'Test notes',
        'flowcell_details': [
            {
                u'machine': u'Unknown',
                u'lane': u'2',
                u'flowcell': u'FC64KEN'
            },
            {
                u'machine': u'Unknown',
                u'lane': u'3',
                u'flowcell': u'FC64M2B'
            }
        ]
    })
    return properties

@pytest.fixture
def replicate_5(root, replicate_url):
    item = root.get_by_uuid(replicate_url['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '4',
        'notes': 'Test notes',
        'platform': 'encode:HiSeq 2000',
        'paired_ended': False,
        'read_length': 36,
        'read_length_units': 'nt'
    })
    return properties
