from .test_audit_experiment import (
    collect_audit_errors
)


def test_audit_annotation_missing_organism(
    testapp, annotation_dataset
):
    res = testapp.get(annotation_dataset['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing organism' for error in errors_list)


def test_audit_annotation_not_uploaded_files(
    testapp, file, annotation_dataset
):
    testapp.patch_json(file['@id'], {
        'status': 'upload failed',
        'dataset': annotation_dataset['@id']
    })
    res = testapp.get(annotation_dataset['@id'] + '@@index-data')
    assert any(error['category'] == 'file validation error'
               for error in collect_audit_errors(res))

    testapp.patch_json(file['@id'], {
        'status': 'content error',
        'content_error_detail': 'test detail',
        'dataset': annotation_dataset['@id']
    })
    res = testapp.get(annotation_dataset['@id'] + '@@index-data')
    assert any(error['category'] == 'file validation error'
               for error in collect_audit_errors(res))


def test_audit_annotation_uploading_files(
    testapp, file, annotation_dataset
):
    testapp.patch_json(file['@id'], {
        'status': 'uploading',
        'dataset': annotation_dataset['@id']
    })
    res = testapp.get(annotation_dataset['@id'] + '@@index-data')
    assert any(error['category'] == 'file in uploading state'
               for error in collect_audit_errors(res))


def test_audit_annotation_derived_from_revoked(
    testapp,
    file,
    annotation_dataset,
    file_with_derived,
    file_with_replicate
):
    testapp.patch_json(file_with_derived['@id'], {'dataset': annotation_dataset['@id']})
    testapp.patch_json(file_with_replicate['@id'], {'status': 'revoked'})
    res = testapp.get(annotation_dataset['@id'] + '@@index-data')
    assert any(error['category'] == 'derived from revoked file'
               for error in collect_audit_errors(res))
