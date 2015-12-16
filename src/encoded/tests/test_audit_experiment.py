import pytest

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""

@pytest.fixture
def library_no_biosample(testapp, lab, award):
    item = {
        'nucleic_acid_term_id': 'SO:0000352',
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
def base_replicate_two(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
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
def fly_organism(testapp):
    item = {
        'taxon_id': "7227",
        'name': "dmelanogaster",
        'scientific_name': "Drosophila melanogaster"
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


@pytest.fixture
def histone_target(testapp, fly_organism):
    item = {
        'organism': fly_organism['uuid'],
        'label': 'Histone',
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def control_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'Control',
        'investigated_as': ['control']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody(testapp, award, lab, source, organism, target):
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
def IgG_antibody(testapp, award, lab, source, organism, control_target):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [control_target['uuid']],
        'product_id': 'ABCDEF',
        'lot_id': '321'
    }
    return testapp.post_json('/antibodies', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization1(testapp, lab, award, target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
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
        'secondary_characterization_method': 'dot blot assay',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def ctrl_experiment(testapp, lab, award, control_target):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': 'OBI:0000716'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


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
def library_1(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]
@pytest.fixture
def library_2(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]

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
def biosample_1(testapp, lab, award, source, organism):
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
def biosample_2(testapp, lab, award, source, organism):
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
def file_fastq(testapp, lab, award, base_experiment, base_replicate):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_bam(testapp, lab, award, base_experiment, base_replicate):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'bam',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'alignments',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


def test_ChIP_possible_control(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep):
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']], 'assay_term_name': 'ChIP-seq', 'assay_term_id': 'OBI:0000716'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'invalid possible_control' for error in errors_list)


def test_audit_input_control(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep, control_target):
    testapp.patch_json(ctrl_experiment['@id'], {'target': control_target['@id']})
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']], 'assay_term_name': 'ChIP-seq', 'assay_term_id': 'OBI:0000716'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing input control' for error in errors_list)


def test_audit_experiment_target(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing target' for error in errors_list)


def test_audit_experiment_replicated(testapp, base_experiment, base_replicate, base_library):    
    testapp.patch_json(base_experiment['@id'], {'status': 'release ready'})      
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'unreplicated experiment' for error in errors_list)

def test_audit_experiment_technical_replicates_same_library(testapp, base_experiment, base_replicate, base_replicate_two, base_library):   
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_replicate_two['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [base_replicate['@id'],base_replicate_two['@id']]})    
    res = testapp.get(base_experiment['@id'] + '@@index-data')    

    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])

    assert any(error['category'] == 'sequencing runs labeled as technical replicates' for error in errors_list)

def test_audit_experiment_biological_replicates_biosample(testapp, base_experiment,base_biosample, library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])        
    assert any(error['category'] == 'biological replicates with identical biosample' for error in errors_list)


def test_audit_experiment_technical_replicates_biosample(testapp, base_experiment, biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_1_2):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])        
    assert any(error['category'] == 'technical replicates with not identical biosample' for error in errors_list)


def test_audit_experiment_with_libraryless_replicated(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'release ready'})
    testapp.patch_json(base_experiment['@id'], {'replicates': [base_replicate['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'replicate with no library' for error in errors_list)


def test_audit_experiment_single_cell_replicated(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'release ready'})    
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'single cell isolation followed by RNA-seq'})    
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'unreplicated experiment' for error in errors_list)


def test_audit_experiment_roadmap_replicated(testapp, base_experiment, base_replicate, base_library, award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'award': award['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'unreplicated experiment' for error in errors_list)


def test_audit_experiment_spikeins(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0001271', 'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_library['@id'], {'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing spikeins_used' for error in errors_list)


def test_audit_experiment_not_tag_antibody(testapp, base_experiment, base_replicate, organism, antibody_lot):
    other_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'eGFP-AVCD', 'investigated_as': ['recombinant protein']}).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': other_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not tagged antibody' for error in errors_list)


def test_audit_experiment_target_tag_antibody(testapp, base_experiment, base_replicate, organism, base_antibody, tag_target):
    ha_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'HA-ABCD', 'investigated_as': ['recombinant protein']}).json['@graph'][0]
    base_antibody['targets'] = [tag_target['@id']]
    tag_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': tag_antibody['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': ha_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched tag target' for error in errors_list)


def test_audit_experiment_target_mismatch(testapp, base_experiment, base_replicate, base_target, antibody_lot):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched target' for error in errors_list)


def test_audit_experiment_eligible_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, antibody_lot, target, base_antibody_characterization1, base_antibody_characterization2):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'], 'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'biosample_term_id': 'EFO:0002067', 'biosample_term_name': 'K562',  'biosample_type': 'immortalized cell line', 
                                                'target': target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not eligible antibody' for error in errors_list)


def test_audit_experiment_eligible_histone_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, base_antibody, histone_target, base_antibody_characterization1, base_antibody_characterization2, fly_organism):
    base_antibody['targets'] = [histone_target['@id']]
    histone_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_biosample['@id'], {'organism': fly_organism['uuid']})
    testapp.patch_json(base_antibody_characterization1['@id'], {'target': histone_target['@id'], 'characterizes': histone_antibody['@id']})
    testapp.patch_json(base_antibody_characterization2['@id'], {'target': histone_target['@id'], 'characterizes': histone_antibody['@id']})
    testapp.patch_json(base_replicate['@id'], {'antibody': histone_antibody['@id'], 'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'biosample_term_id': 'EFO:0002067', 'biosample_term_name': 'K562',  'biosample_type': 'immortalized cell line', 'target': 
                                                histone_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not eligible antibody' for error in errors_list)


def test_audit_experiment_biosample_type_missing(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': "EFO:0002067", 'biosample_term_name': 'K562'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing biosample_type' for error in errors_list)


def test_audit_experiment_documents(testapp, base_experiment, base_library, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing documents' for error in errors_list)


def test_audit_experiment_model_organism_mismatched_sex(testapp,
                                                        base_experiment,
                                                        replicate_1_1,
                                                        replicate_2_1,
                                                        library_1,
                                                        library_2,
                                                        biosample_1,
                                                        biosample_2,
                                                        mouse_donor_1):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'male'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'female'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched sex' for error in errors_list)


def test_audit_experiment_model_organism_mismatched_age(testapp,
                                                        base_experiment,
                                                        replicate_1_1,
                                                        replicate_2_1,
                                                        library_1,
                                                        library_2,
                                                        biosample_1,
                                                        biosample_2,
                                                        mouse_donor_1,
                                                        mouse_donor_2):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '51'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched age' for error in errors_list)


def test_audit_experiment_model_organism_mismatched_donor(testapp,
                                                          base_experiment,
                                                          replicate_1_1,
                                                          replicate_2_1,
                                                          library_1,
                                                          library_2,
                                                          biosample_1,
                                                          biosample_2,
                                                          mouse_donor_1,
                                                          mouse_donor_2):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_2['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched donor' for error in errors_list)


def test_audit_experiment_with_library_without_biosample(testapp, base_experiment, base_replicate,
                                                         library_no_biosample):
    testapp.patch_json(base_replicate['@id'], {'library': library_no_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing biosample' for error in errors_list)


def test_audit_experiment_with_RNA_library_no_size_range(testapp, base_experiment, base_replicate,
                                                         base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_id':
                                             'SO:0000356', 'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing size_range' for error in errors_list)


def test_audit_experiment_with_RNA_library_with_size_range(testapp, base_experiment, base_replicate,
                                                           base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_id': 'SO:0000356',
                                             'nucleic_acid_term_name': 'RNA', 'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing size_range' for error in errors_list)


def test_audit_experiment_with_RNA_library_array_size_range(testapp, base_experiment,
                                                            base_replicate,
                                                            base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_id': 'SO:0000356',
                                             'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'transcription profiling by array assay'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing size_range' for error in errors_list)


def test_audit_experiment_biosample_term_id(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': 'CL:349829',
                                                'biosample_type': 'tissue',
                                                'status': 'released'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'experiment with invalid biosample term id' for error in errors_list)


def test_audit_experiment_replicate_with_file(testapp, file_fastq,
                                              base_experiment,
                                              base_replicate,
                                              base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(((error['category'] != 'missing file in replicate') and
               (error['category'] != 'missing FASTQ file in replicate')) for error in errors_list)


def test_audit_experiment_replicate_with_no_files(testapp,
                                                  base_experiment,
                                                  base_replicate,
                                                  base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing file in replicate' for error in errors_list)


def test_audit_experiment_missing_biosample_term_id(testapp, base_experiment):
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'experiment missing biosample_term_id' for error in errors_list)


def test_audit_experiment_replicate_with_no_fastq_files(testapp, file_bam,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing FASTQ file in replicate' for error in errors_list)
