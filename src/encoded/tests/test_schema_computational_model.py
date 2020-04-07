import pytest

def test_verify_software_is_unique(testapp, computational_model_url):
    res = testapp.get(computational_model_url['@id'] + '@@index-data')
    data = res.json;
    import pdb; pdb.set_trace()
    values = res.json['properties']
    software_used_list = values['software_used']
    assert len(set(software_used_list)) == len(software_used_list)


def test_verify_identical_used_software_fails(testapp, computational_model_for_dup_software_used_url):
        res = testapp.get(computational_model_url['@id'] + '@@index-data')
        data = res.json;
        import pdb; pdb.set_trace()
        values = res.json['properties']
        software_used_list = values['software_used']
        assert len(set(software_used_list)) == len(software_used_list)
