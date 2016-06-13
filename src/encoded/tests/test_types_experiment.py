import pytest

@pytest.fixture
def base_experiment(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'started'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

def test_isogenic_replicate_type(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='isogenic' 

def test_anisogenic_replicate_type_sex_age_matched(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'female' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic' 

def test_anisogenic_replicate_type_sex_matched(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '15' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'female' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic' 

def test_anisogenic_replicate_type_age_matched(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'mixed' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic'     

def test_anisogenic_replicate_type(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age': 'unknown' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55' })
    testapp.patch_json(donor_1['@id'], {'sex': 'female' })
    testapp.patch_json(donor_2['@id'], {'sex': 'unknown' })    
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id']})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'], replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data') 
    assert res.json['object']['replication_type']=='anisogenic'     