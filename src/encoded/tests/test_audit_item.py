def test_audit_item_schema_validation(testapp, organism):
    testapp.patch_json(organism['@id'] +
                       '?validate=false', {'disallowed': 'errs'})
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(
        error['category'] == 'validation error' and error['name'] == 'audit_item_schema'
        for error in errors_list)


def test_audit_item_schema_upgrade_failure(testapp, organism):
    testapp.patch_json(organism['@id'] +
                       '?validate=false', {'schema_version': '999'})
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(
        error['category'] == 'upgrade failure' and error['name'] == 'audit_item_schema'
        for error in errors_list)


def test_audit_item_schema_upgrade_ok(testapp, organism):
    patch = {
        'schema_version': '1',
        'status': 'CURRENT',
    }
    testapp.patch_json(organism['@id'] + '?validate=false', patch)
    res = testapp.get(organism['@id'] + '@@index-data')
    # errors = [e for e in res.json['audit'] if e['name'] == 'audit_item_schema']
    # assert not errors
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert not any(error['name'] ==
                   'audit_item_schema' for error in errors_list)


def test_audit_item_schema_upgrade_validation_failure(testapp, organism):
    patch = {
        'schema_version': '1',
        'status': 'UNKNOWN',
    }
    testapp.patch_json(organism['@id'] + '?validate=false', patch)
    res = testapp.get(organism['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(
        error['category'] == 'validation error: status' and error['name'] == 'audit_item_schema'
        for error in errors_list)


def test_audit_item_schema_permission(testapp, file, embed_testapp):
    # Redmine 2915
    patch = {
        'file_format': '2bit',
        'status': 'deleted',
    }
    testapp.patch_json(file['@id'], patch)
    res = embed_testapp.get(file['@id'] + '/@@audit-self')
    errors_list = res.json['audit']
    assert not any(error['name'] ==
                   'audit_item_schema' for error in errors_list)


def test_audit_item_status_level_dict_contains_all_statuses_in_schema(testapp):
    # This checks that STATUS_LEVEL dict contains all statuses enumerated in schema.
    from ..audit.item import STATUS_LEVEL
    status_level_keys = STATUS_LEVEL.keys()
    schemas = testapp.get('/profiles/').json
    for title, schema in schemas.items():
        # Assumes all statuses are in properties.status.enum.
        schema_statuses = schema.get(
            'properties', {}).get('status', {}).get('enum')
        # Missing derived_from file audit relies on STATUS_LEVEL dict from audit/item.py.
        # This dict should not get out of sync with allowable statuses in file schema.
        # Explicit check that file statuses found:
        if title == 'File':
            # If this assertion fails update file schema path to statuses above.
            assert schema_statuses is not None, 'File status enum not found.'
        if schema_statuses is not None:
            print(title)
            # Statuses that are in schema but not in STATUS_LEVEL.
            schema_dict_diff = set(schema_statuses) - set(status_level_keys)
            # If this assertion fails update STATUS_LEVEL dict with new statuses in schema.
            assert not schema_dict_diff, '{} in {} schema but not in STATUS_LEVEL dict.'.format(
                schema_dict_diff, title)
