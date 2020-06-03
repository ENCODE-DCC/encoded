import pytest


@pytest.fixture
def library_no_biosample(testapp, lab, award):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id']
    }
    return testapp.post_json('/library', item).json['@graph'][0]


@pytest.fixture
def base_library(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_1(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_2(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library(lab, award):
    return {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'nucleic_acid_term_name': 'DNA'
    }


@pytest.fixture
def library_url(testapp, lab, award, biosample):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id'],
        'biosample': biosample['@id'],
    }
    return testapp.post_json('/library', item).json['@graph'][0]


@pytest.fixture
def library_starting_quantity(library):
    item = library.copy()
    item.update({
        'nucleic_acid_starting_quantity': '10',
        'nucleic_acid_starting_quantity_units': 'ng',
    })
    return item


@pytest.fixture
def library_starting_quantity_no_units(library):
    item = library.copy()
    item.update({
        'nucleic_acid_starting_quantity': '10',
    })
    return item

@pytest.fixture
def library_with_invalid_fragmentation_methods_string(library):
    item = library.copy()
    item.update(
        {
            'fragmentation_methods': 'chemical (DpnII restriction)',
        }
    )
    return item

@pytest.fixture
def library_with_valid_fragmentation_method_list(library):
    item = library.copy()
    item.update(
        {
            'fragmentation_methods': ['chemical (DpnII restriction)', 'chemical (HindIII restriction)'],
        }
    )
    return item


@pytest.fixture
def library_0_0(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
    }


@pytest.fixture
def library_1_0(library_0_0):
    item = library_0_0.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def library_2_0(library_0_0):
    item = library_0_0.copy()
    item.update({
        'schema_version': '3',
        'paired_ended': False
    })
    return item


@pytest.fixture
def library_3_0(library_0_0):
    item = library_0_0.copy()
    item.update({
        'schema_version': '3',
        'fragmentation_method': 'covaris sheering'
    })
    return item


@pytest.fixture
def library_8_0(library_3_0):
    item = library_3_0.copy()
    item.update({
        'schema_version': '8',
        'status': "in progress"
    })
    return item


@pytest.fixture
def library_schema_9(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'extraction_method': 'Trizol (Invitrogen 15596-026)',
        'lysis_method': 'Possibly Trizol',
        'library_size_selection_method': 'Gel',
    }


@pytest.fixture
def library_schema_9b(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'extraction_method': 'see document ',
        'lysis_method': 'test',
    }


@pytest.fixture
def library_schema_10(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'strand_specificity': True
    }


@pytest.fixture
def library_1_chip(testapp, lab, award, biosample_human_1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample': biosample_human_1['@id'],
        'nucleic_acid_term_name': 'DNA'
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_2_chip(testapp, lab, award, biosample_human_2):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample': biosample_human_2['@id'],
        'nucleic_acid_term_name': 'DNA'
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_size_range(library):
    item = library.copy()
    item.update({
        'size_range': '100-800',
    })
    return item


@pytest.fixture
def library_fragment_length_CV(library):
    item = library.copy()
    item.update({
        'fragment_length_CV': 68,
    })
    return item


@pytest.fixture
def library_schema_11a(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'fragmentation_methods': ['chemical (HindIII/DpnII restriction)', 'shearing (generic)']
    }


@pytest.fixture
def library_schema_11b(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'fragmentation_methods': ['chemical (HindIII/DpnII restriction)', 'chemical (DpnII restriction)', 'shearing (generic)']
    }


@pytest.fixture
def library_schema_12(library, award, lab, biosample_human_2):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample': biosample_human_2['@id'],
        'nucleic_acid_term_name': 'DNA',
        'adapters': [
            {
              'type': '3\' adapter',
              'sequence': 'ACCCCTG'
            },
            {
              'sequence': 'GGGGGGCN'
            }
        ]
    }
