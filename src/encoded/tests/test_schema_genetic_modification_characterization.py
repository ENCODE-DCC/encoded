import pytest

def test_characterization_review_dependency(testapp, attachment, submitter, construct_genetic_modification_N, lab, award):
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'lab': lab['@id'],
            'status': 'compliant'
        }
    }
    testapp.post_json('/genetic_modification_characterization', item, status=422)
    item['review'] = {'lab' : lab['@id']}
    testapp.post_json('/genetic_modification_characterization', item, status=201)
    item['review'] = {'lab' : lab['@id'], 'lane': 4, 'reviewed_by': submitter['@id'], 'status': 'not compliant'}
    testapp.post_json('/genetic_modification_characterization', item, status=201)