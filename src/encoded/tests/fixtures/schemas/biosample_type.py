import pytest


@pytest.fixture
def heart(testapp):
    item = {
        'term_id': 'UBERON:0000948',
        'term_name': 'heart',
        'classification': 'tissue',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


@pytest.fixture
def cell_free(testapp):
    item = {
        'term_id': 'NTR:0000471',
        'term_name': 'cell-free sample',
        'classification': 'cell-free sample',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


@pytest.fixture
def ntr_biosample_type(testapp):
    item = {
        'term_id': 'NTR:0000022',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def id_nonexist_biosample_type(testapp):
    item = {
        'term_id': 'CL:99999999',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def purkinje_cell(testapp):
    item = {
            'term_id': "CL:0000121",
            'term_name': 'Purkinje cell',
            'classification': 'primary cell'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def cerebellum(testapp):
    item = {
            'term_id': "UBERON:0002037",
            'term_name': 'cerebellum',
            'classification': 'tissue'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def organoid(testapp):
    item = {
            'term_id': 'UBERON:0000955',
            'term_name': 'brain',
            'classification': 'organoid'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def a549(testapp):
    item = {
        'term_id': 'EFO:0001086',
        'term_name': 'A549',
        'classification': 'cell line',
        'dbxrefs': ['Cellosaurus:CVCL_0023']
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_type(a549):
    return a549


@pytest.fixture
def k562(testapp):
    item = {
        'term_id': 'EFO:0001086',
        'term_name': 'K562',
        'classification': 'cell line',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def hepg2(testapp):
    item = {
        'term_id': 'EFO:0001187',
        'term_name': 'HepG2',
        'classification': 'cell line',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def mel(testapp):
    item = {
            'term_name': 'MEL cell line',
            'term_id': 'EFO:0003971',
            'classification': 'cell line',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def h1(testapp):
    item = {
            'term_id': "EFO:0003042",
            'term_name': 'H1-hESC',
            'classification': 'cell line'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def ileum(testapp):
    item = {
            'term_id': "UBERON:0002116",
            'term_name': 'ileum',
            'classification': 'tissue'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def brain(testapp):
    item = {
            'term_id': "UBERON:0000955",
            'term_name': 'brain',
            'classification': 'tissue'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def whole_organism(testapp):
    item = {
            'uuid': '25d5ad53-15fd-4a44-878a-ece2f7e86509',
            'term_id': "UBERON:0000468",
            'term_name': 'multi-cellular organism',
            'classification': 'whole organisms'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def erythroblast(testapp):
    item = {
            'term_id': "CL:0000765",
            'term_name': 'erythroblast',
            'classification': 'primary cell'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def gm12878(testapp):
    item = {
            'term_id': "EFO:0002784",
            'term_name': 'GM12878',
            'classification': 'cell line'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def s2r_plus(testapp):
    item = {
            'term_id': "EFO:0005837",
            'term_name': 'S2R+',
            'classification': 'cell line'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def single_cell(testapp):
    item = {
            'term_id': "UBERON:349829",
            'term_name': 'heart',
            'classification': 'single cell'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def inconsistent_biosample_type(testapp):
    item = {
        'term_id': 'EFO:0002067',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def liver(testapp):
    item = {
        'term_id': 'UBERON:0002107',
        'term_name': 'liver',
        'classification': 'tissue',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


@pytest.fixture
def cloning_sample(testapp):
    item = {
        'term_id': 'NTR:0000545',
        'term_name': 'DNA cloning sample',
        'classification': 'cloning host',
        'uuid': '09e6c39a-92af-41fc-a535-7a86d5e9590a'
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


@pytest.fixture
def epiblast(testapp):
    item = {
        'term_id': 'CL:0000352',
        'term_name': 'epiblast cell',
        'classification': 'in vitro differentiated cells',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]
