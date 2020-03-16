import pytest


def _remote_user_testapp(app, remote_user):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': str(remote_user),
    }
    return TestApp(app, environ)


@pytest.fixture
def remote_user_testapp(app, remote_user):
    return _remote_user_testapp(app, remote_user)


@pytest.fixture
def wrangler_testapp(wrangler, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, wrangler['uuid'])


@pytest.fixture
def submitter_testapp(submitter, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, submitter['uuid'])


@pytest.fixture
def viewing_group_member_testapp(viewing_group_member, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, viewing_group_member['uuid'])


@pytest.fixture
def remc_member_testapp(remc_member, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, remc_member['uuid'])


@pytest.fixture
def indexer_testapp(app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, 'INDEXER')


def test_wrangler_post_non_lab_collection(wrangler_testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return wrangler_testapp.post_json('/organism', item, status=201)


def test_submitter_post_non_lab_collection(submitter_testapp):
    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return submitter_testapp.post_json('/organism', item, status=403)


def test_submitter_post_update_experiment(submitter_testapp, lab, award, cell_free):
    experiment = {'lab': lab['@id'],
                  'award': award['@id'],
                  'assay_term_name': 'RNA-seq',
                  'biosample_ontology': cell_free['uuid']}
    res = submitter_testapp.post_json('/experiment', experiment, status=201)
    location = res.location
    res = submitter_testapp.get(location + '@@testing-allowed?permission=edit', status=200)
    assert res.json['has_permission'] is True
    assert 'submits_for.%s' % lab['uuid'] in res.json['principals_allowed_by_permission']
    submitter_testapp.patch_json(location, {'description': 'My experiment'}, status=200)


def test_submitter_post_other_lab(submitter_testapp, other_lab, award, cell_free):
    experiment = {'lab': other_lab['@id'],
                  'award': award['@id'],
                  'assay_term_name': 'RNA-seq',
                  'biosample_ontology': cell_free['uuid']}
    res = submitter_testapp.post_json('/experiment', experiment, status=422)
    assert "not in user submits_for" in res.json['errors'][0]['description']


def test_not_reviewer_patch_other_lab_characterization(submitter_testapp, testapp, submitter, attachment, construct_genetic_modification_N, other_lab, lab, award):
    testapp.patch_json(submitter['@id'], {'submits_for': [other_lab['@id']]}),
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'lab': lab['@id']
        }
        
    }
    gm = testapp.post_json('/genetic_modification_characterization', item).json['@graph'][0]
    res = submitter_testapp.patch_json(
        gm['@id'],
        {'review': {'lab': lab['@id'],
                    'lane': 3, 
                    'reviewed_by': submitter['@id'],
                    'status': 'compliant'}}, expect_errors=True)
    assert "not in user submits_for" in res.json['errors'][0]['description']


def test_reviewer_patch_other_lab_characterization(submitter_testapp, testapp, submitter, attachment, construct_genetic_modification_N, other_lab, lab, award):
    testapp.patch_json(submitter['@id'], {'submits_for': [other_lab['@id']]}),
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'review': {
            'lab': other_lab['@id']
        }
    }
    gm = testapp.post_json('/genetic_modification_characterization', item).json['@graph'][0]
    submitter_testapp.patch_json(
        gm['@id'],
        {'review': {'lab': other_lab['@id'], 'lane': 2, 'reviewed_by': submitter['@id'], 'status': 'compliant'}}, status=200)


def test_not_submitted_for_review_antibody_characterizations_view_basic_anon(antibody_characterization_url, testapp, anontestapp):
    testapp.patch_json(antibody_characterization_url['@id'], {"status": "not submitted for review by lab"})
    anontestapp.get(antibody_characterization_url['@id'], status=200)


def test_in_progress_antibody_characterizations_view_basic_anon(antibody_characterization_url, testapp, anontestapp):
    anontestapp.get(antibody_characterization_url['@id'], status=403)


def test_wrangler_post_other_lab(wrangler_testapp, other_lab, award, cell_free):
    experiment = {'lab': other_lab['@id'],
                  'award': award['@id'],
                  'assay_term_name': 'RNA-seq',
                  'biosample_ontology': cell_free['uuid']}
    wrangler_testapp.post_json('/experiment', experiment, status=201)


def test_user_view_details_admin(submitter, access_key_2, testapp):
    res = testapp.get(submitter['@id'])
    assert 'email' in res.json
    assert 'access_keys' in res.json
    assert 'access_key_id' in res.json['access_keys'][0]


def test_users_view_details_self(submitter, access_key_2, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    assert 'email' in res.json
    assert 'access_keys' in res.json
    assert 'access_key_id' in res.json['access_keys'][0]


def test_users_patch_self(submitter, access_key, submitter_testapp):
    submitter_testapp.patch_json(submitter['@id'], {})


def test_users_post_disallowed(submitter, access_key, submitter_testapp):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter2',
        'email': 'encode_submitter2@example.org',
    }
    submitter_testapp.post_json('/user', item, status=403)


def test_users_view_basic_authenticated(submitter, authenticated_testapp):
    res = authenticated_testapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json
    assert 'access_keys' not in res.json


def test_users_view_basic_anon(submitter, anontestapp):
    res = anontestapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json
    assert 'access_keys' not in res.json


def test_users_view_basic_indexer(submitter, indexer_testapp):
    res = indexer_testapp.get(submitter['@id'])
    assert 'title' in res.json
    assert 'email' not in res.json
    assert 'access_keys' not in res.json


def test_viewing_group_member_view(viewing_group_member_testapp, experiment):
    viewing_group_member_testapp.get(experiment['@id'], status=200)


def test_remc_member_view_disallowed(remc_member_testapp, experiment):
    remc_member_testapp.get(experiment['@id'], status=403)


def test_remc_member_view_shared(remc_member_testapp, mouse_donor):
    remc_member_testapp.get(mouse_donor['@id'], status=200)


def test_submitter_patch_lab_disallowed(submitter, other_lab, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    lab = {'lab': other_lab['@id']}
    submitter_testapp.patch_json(res.json['@id'], lab, status=422)  # is that the right status?


def test_wrangler_patch_lab_allowed(submitter, other_lab, wrangler_testapp):
    res = wrangler_testapp.get(submitter['@id'])
    lab = {'lab': other_lab['@id']}
    wrangler_testapp.patch_json(res.json['@id'], lab, status=200)


def test_submitter_patch_submits_for_disallowed(submitter, other_lab, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    submits_for = {'submits_for': res.json['submits_for'] + [other_lab['@id']]}
    submitter_testapp.patch_json(res.json['@id'], submits_for, status=422)


def test_wrangler_patch_submits_for_allowed(submitter, other_lab, wrangler_testapp):
    res = wrangler_testapp.get(submitter['@id'])
    submits_for = {'submits_for': res.json['submits_for'] + [other_lab['@id']]}
    wrangler_testapp.patch_json(res.json['@id'], submits_for, status=200)


def test_submitter_patch_groups_disallowed(submitter, other_lab, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    groups = {'groups': res.json['groups'] + ['admin']}
    submitter_testapp.patch_json(res.json['@id'], groups, status=422)


def test_wrangler_patch_groups_allowed(submitter, other_lab, wrangler_testapp):
    res = wrangler_testapp.get(submitter['@id'])
    groups = {'groups': res.json['groups'] + ['admin']}
    wrangler_testapp.patch_json(res.json['@id'], groups, status=200)


def test_submitter_patch_viewing_groups_disallowed(submitter, other_lab, submitter_testapp):
    res = submitter_testapp.get(submitter['@id'])
    vgroups = {'viewing_groups': res.json['viewing_groups'] + ['GGR']}
    submitter_testapp.patch_json(res.json['@id'], vgroups, status=422)


def test_wrangler_patch_viewing_groups_allowed(submitter, other_lab, wrangler_testapp):
    res = wrangler_testapp.get(submitter['@id'])
    vgroups = {'viewing_groups': res.json['viewing_groups'] + ['GGR']}
    wrangler_testapp.patch_json(res.json['@id'], vgroups, status=200)


def test_disabled_user_denied_authenticated(authenticated_testapp, disabled_user):
    authenticated_testapp.get(disabled_user['@id'], status=403)


def test_disabled_user_denied_submitter(submitter_testapp, disabled_user):
    submitter_testapp.get(disabled_user['@id'], status=403)


def test_disabled_user_wrangler(wrangler_testapp, disabled_user):
    wrangler_testapp.get(disabled_user['@id'], status=200)


def test_labs_view_wrangler(wrangler_testapp, other_lab):
    labs = wrangler_testapp.get('/labs/', status=200)
    assert(len(labs.json['@graph']) == 1)


def test_post_qc_metric(wrangler_testapp, step_run, file, lab, award):
    item = {
        'name': 'test-quality-metric',
        'quality_metric_of': [file['@id']],
        'step_run': step_run['@id'],
        'lab': lab['@id'],
        'award': award['@id']
    }
    wrangler_testapp.post_json('/generic-quality-metrics', item, status=201)


def test_submitter_post_qc_metric(submitter_testapp, step_run, file, lab, award):
    item = {
        'name': 'test-quality-metric',
        'quality_metric_of': [file['@id']],
        'step_run': step_run['@id'],
        'lab': lab['@id'],
        'award': award['@id']
    }
    submitter_testapp.post_json('/generic-quality-metrics', item, status=201)


def test_wronggroup_post_qc_metric(remc_member_testapp, step_run, file, remc_lab, award):
    item = {
        'name': 'test-quality-metric',
        'quality_metric_of': [file['@id']],
        'step_run': step_run['@id'],
        'lab': remc_lab['@id'],
        'award': award['@id']
    }
    remc_member_testapp.post_json('/generic-quality-metrics', item, status=403)


def test_experiment_submitter_no_edit_status(submitter_testapp, lab, award, experiment):
    submitter_testapp.patch_json(experiment['@id'], {'status': 'submitted'}, status=422)