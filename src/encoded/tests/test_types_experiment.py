import pytest

@pytest.fixture
def base_experiment(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_type': 'in vitro sample',
        'status': 'started'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

def test_isogenic_replicate_type(testapp, base_experiment, donor_1, donor_2,biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_2_1 ):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
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
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
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
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '15', 'life_stage': 'adult' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
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
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
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
    testapp.patch_json(donor_2['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult' })
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

def test_experiment_biosample_summary(testapp,
                                      base_experiment,
                                      donor_1,
                                      donor_2,
                                      biosample_1,
                                      biosample_2,
                                      library_1,
                                      library_2,
                                      treatment,
                                      replicate_1_1,
                                      replicate_2_1):
    testapp.patch_json(donor_1['@id'], {'age_units': 'year', 'age': '55', 'life_stage': 'adult'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'day', 'age': '1', 'life_stage': 'child'})
    testapp.patch_json(donor_1['@id'], {'sex': 'female',
                                        "life_stage": "embryonic"})
    testapp.patch_json(donor_2['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            'treatments': [treatment['@id']],
                                            "biosample_term_id": "EFO:0005837",
                                            "biosample_term_name": "S2R+",
                                            "biosample_type": "immortalized cell line",
                                            "subcellular_fraction_term_name": "nucleus",
                                            })
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            "biosample_term_id": "UBERON:0002784",
                                            "biosample_term_name": "liver",
                                            "biosample_type": "tissue",
                                            'treatments': [treatment['@id']]})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'S2R+ nuclear fraction and ' + \
        'liver male child (1 day), treated with ethanol'


def test_experiment_biosample_summary_2(testapp,
                                        base_experiment,
                                        donor_1,
                                        donor_2,
                                        biosample_1,
                                        biosample_2,
                                        library_1,
                                        library_2,
                                        treatment,
                                        replicate_1_1,
                                        replicate_2_1):
    testapp.patch_json(donor_1['@id'], {'age_units': 'day', 'age': '10', 'life_stage': 'child'})
    testapp.patch_json(donor_2['@id'], {'age_units': 'day', 'age': '10', 'life_stage': 'child'})
    testapp.patch_json(donor_1['@id'], {'sex': 'male'})
    testapp.patch_json(donor_2['@id'], {'sex': 'male'})
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            "biosample_term_id": "UBERON:0002784",
                                            "biosample_term_name": "liver",
                                            "biosample_type": "tissue",
                                            'treatments': [treatment['@id']]})

    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            "biosample_term_id": "UBERON:0002784",
                                            "biosample_term_name": "liver",
                                            "biosample_type": "tissue"})

    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [replicate_1_1['@id'],
                                                               replicate_2_1['@id']]})
    res = testapp.get(base_experiment['@id']+'@@index-data')
    assert res.json['object']['biosample_summary'] == \
        'liver male child (10 days) not treated and treated with ethanol'
