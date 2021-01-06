import pytest


@pytest.fixture
def award_base(testapp):
    item = {
        'name': 'seed-network-award',
        'project': 'HCA Seed Networks',
        'title': 'A Generic HCA Award',
        'uuid': '62ba2fba-8ee9-4996-b804-f9a673d137c3',
        'viewing_groups': ['CZI004LIV']
    }
    return testapp.post_json('/award', item).json['@graph'][0]
