import pytest


def test_post_target_organism(testapp, target_nongene, target_one_gene,
                              target_two_same_org, target_two_diff_orgs,
                              target_genes_org):
    testapp.post_json('/target', target_nongene, status=201)
    testapp.post_json('/target', target_one_gene, status=201)
    testapp.post_json('/target', target_two_same_org, status=201)
    testapp.post_json('/target', target_two_diff_orgs, status=422)
    testapp.post_json('/target', target_genes_org, status=422)

    # Make sure target two-diff-org and genes-org didn't get into database
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 3


def test_patch_target_two_diff_orgs(testapp, target_nongene, target_one_gene,
                                    target_two_same_org, target_two_diff_orgs):
    # Nongene target to target with two genes from different organisms
    old_target = testapp.post_json('/target', target_nongene).json['@graph'][0]
    testapp.put_json(old_target['@id'], target_two_diff_orgs, status=422)
    res = testapp.get(old_target['@id'] + '?datastore=database')
    assert 'genes' not in res.json
    assert 'target_organism' in res.json

    # One gene target to target with two genes from different organisms
    old_target = testapp.post_json('/target', target_one_gene).json['@graph'][0]
    testapp.patch_json(old_target['@id'], target_two_diff_orgs, status=422)
    res = testapp.get(old_target['@id'] + '?datastore=database')
    assert set(g['uuid'] for g in res.json['genes']) == set(target_one_gene['genes'])

    # Two gene target to target with two genes from different organisms
    old_target = testapp.post_json('/target', target_two_same_org).json['@graph'][0]
    testapp.patch_json(old_target['@id'], target_two_diff_orgs, status=422)
    res = testapp.get(old_target['@id'] + '?datastore=database')
    assert set(g['uuid'] for g in res.json['genes']) == set(target_two_same_org['genes'])


def test_nongene_to_onegene(testapp, target_nongene, target_one_gene):
    nongene = testapp.post_json('/target', target_nongene).json['@graph'][0]
    res = testapp.put_json(nongene['@id'], target_one_gene, status=200)
    res = testapp.get(res.json['@graph'][0]['@id'] + '?datastore=database')
    assert set(g['uuid'] for g in res.json['genes']) == set(target_one_gene['genes'])
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 1


def test_nongene_to_twogenes(testapp, target_nongene, target_two_same_org):
    nongene = testapp.post_json('/target', target_nongene).json['@graph'][0]
    res = testapp.put_json(nongene['@id'], target_two_same_org, status=200)
    res = testapp.get(res.json['@graph'][0]['@id'] + '?datastore=database')
    assert set(g['uuid'] for g in res.json['genes']) == set(target_two_same_org['genes'])
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 1


def test_onegene_to_nongene(testapp, target_one_gene, target_nongene):
    onegene = testapp.post_json('/target', target_one_gene).json['@graph'][0]
    res = testapp.put_json(onegene['@id'], target_nongene, status=200)
    res = testapp.get(res.json['@graph'][0]['@id'] + '?datastore=database')
    assert 'genes' not in res.json
    assert 'target_organism' in res.json
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 1


def test_onegene_to_twogenes(testapp, target_one_gene, target_two_same_org):
    onegene = testapp.post_json('/target', target_one_gene).json['@graph'][0]
    res = testapp.patch_json(onegene['@id'], target_two_same_org, status=200)
    res = testapp.get(res.json['@graph'][0]['@id'] + '?datastore=database')
    assert set(g['uuid'] for g in res.json['genes']) == set(target_two_same_org['genes'])
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 1


def test_twogenes_to_nongene(testapp, target_two_same_org, target_nongene):
    twogenes = testapp.post_json('/target', target_two_same_org).json['@graph'][0]
    res = testapp.put_json(twogenes['@id'], target_nongene, status=200)
    res = testapp.get(res.json['@graph'][0]['@id'] + '?datastore=database')
    assert 'genes' not in res.json
    assert 'target_organism' in res.json
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 1


def test_twogenes_to_onegene(testapp, target_two_same_org, target_one_gene):
    twogenes = testapp.post_json('/target', target_two_same_org).json['@graph'][0]
    res = testapp.patch_json(twogenes['@id'], target_one_gene, status=200)
    res = testapp.get(res.json['@graph'][0]['@id'] + '?datastore=database')
    assert set(g['uuid'] for g in res.json['genes']) == set(target_one_gene['genes'])
    res = testapp.get('/targets/?datastore=database')
    assert len(res.json['@graph']) == 1


def test_target_organism_at_id(testapp, human):
    item = {
        'label': 'target_organism-at-id',
        'target_organism': human['@id'],
        'investigated_as': ['other context'],
    }
    res = testapp.post_json('/target', item).json['@graph'][0]
    assert res['organism'] == human['@id']


def test_target_organism_uuid(testapp, human):
    item = {
        'label': 'target_organism-uuid',
        'target_organism': human['uuid'],
        'investigated_as': ['other context'],
    }
    res = testapp.post_json('/target', item).json['@graph'][0]
    assert res['organism'] == human['@id']


def test_synthetic_tag_target(testapp, target_synthetic_tag, human, ctcf):
    flag_target = testapp.post_json(
        '/target', target_synthetic_tag
    ).json['@graph'][0]
    assert flag_target['title'] == 'FLAG (Synthetic tag)'
    two_investigations_with_synthetic = {
        'investigated_as': ['transcription factor', 'synthetic tag']
    }
    testapp.patch_json(flag_target['@id'], two_investigations_with_synthetic,
                       status=422)

    syn_and_org = {'target_organism': human['uuid']}
    syn_and_org.update(target_synthetic_tag)
    testapp.post_json('/target', syn_and_org, status=422)
    syn_and_org['investigated_as'] = ['synthetic tag', 'tag']
    testapp.post_json('/target', syn_and_org, status=422)

    syn_and_gene = {'genes': [ctcf['uuid']]}
    syn_and_gene.update(target_synthetic_tag)
    testapp.post_json('/target', syn_and_gene, status=422)
    syn_and_gene['investigated_as'] = ['synthetic tag', 'tag']
    testapp.post_json('/target', syn_and_gene, status=422)
