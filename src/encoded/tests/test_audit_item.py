def test_audit_item_schema_validation(testapp, organism):
    testapp.patch_json(organism['@id'] + '?validate=false', {'disallowed': 'errs'})
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'validation error' for error in errors)


def test_audit_item_schema_upgrade_failure(testapp, organism):
    testapp.patch_json(organism['@id'] + '?validate=false', {'schema_version': '999'})
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'upgrade failure' for error in errors)


def test_audit_item_schema_upgrade_ok(testapp, organism):
    patch = {
        'schema_version': '1',
        'status': 'CURRENT',
    }
    testapp.patch_json(organism['@id'] + '?validate=false', patch)
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    assert not errors


def test_audit_item_schema_upgrade_validation_failure(testapp, organism):
    patch = {
        'schema_version': '1',
        'status': 'UNKNOWN',
    }
    testapp.patch_json(organism['@id'] + '?validate=false', patch)
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(error['category'] == 'validation error: status' for error in errors)
