import pytest


@pytest.fixture
def disabled_user(testapp, lab_base):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter',
        'email': 'no_login_submitter@example.org',
        'submits_for': [lab_base['@id']],
        'status': 'disabled',
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def user_base():
    return{
        'first_name': 'Benjamin',
        'last_name': 'Hitz',
        'email': 'hitz@stanford.edu',
    }


@pytest.fixture
def user_1(user_0_0):
    item = user_0_0.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT'
    })
    return item


def test_user_upgrade(upgrader, user_1):
    value = upgrader.upgrade('user', user_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'current'


@pytest.fixture
def user_3(user_0_0):
    item = user_0_0.copy()
    item.update({
        'schema_version': '3',
        'viewing_groups': ['CZI038TEN'],
    })
    return item


@pytest.fixture
def user_7(user_0_0):
    item = user_0_0.copy()
    item.update({
        'schema_version': '6',
        'phone1': '206-685-2672',
        'phone2': '206-267-1098',
        'fax': '206-267-1094',
        'skype': 'fake_id',
        'google': 'google',
        'timezone': 'US/Pacific',
    })
    return item


@pytest.fixture
def user_8(user_0_0):
    item = user_0_0.copy()
    item.update({
        'schema_version': '8',
        'viewing_groups': ['CZI003CNS'],
        'groups': ['admin', 'verified', 'wrangler'],
    })
    return item


@pytest.fixture
def admin(testapp):
    item = {
        'first_name': 'Test',
        'last_name': 'Admin',
        'email': 'admin@example.org',
        'groups': ['admin'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def wrangler(testapp):
    item = {
        # antibody_characterization reviewed_by has linkEnum
        'uuid': '4c23ec32-c7c8-4ac0-affb-04befcc881d4',
        'first_name': 'Wrangler',
        'last_name': 'Admin',
        'email': 'wrangler@example.org',
        'groups': ['admin'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def verified_member(testapp):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'VerifiedMember',
        'email': 'Verified_member@example.org',
        'groups': ['verified'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def unverified_member(testapp):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'NonVerifiedMember',
        'email': 'Non_verified_member@example.org',
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def submitter(testapp, lab_base):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter',
        'email': 'encode_submitter@example.org',
        'submits_for': [lab_base['@id']],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def viewing_group_member(testapp, award_base):
    item = {
        'first_name': 'Viewing',
        'last_name': 'Group',
        'email': 'viewing_group_member@example.org',
        'viewing_groups': award_base['viewing_groups'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json
