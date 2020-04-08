import pytest


def test_audit_library_barcode_details(testapp, library_url, biosample, single_cell):
    testapp.patch_json(library_url['@id'], {'barcode_details': [{'barcode': 'ATTTCGC'}]})
    res = testapp.get(library_url['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent barcode details'
               for error in errors_list)
    testapp.patch_json(biosample['@id'], {'biosample_ontology': single_cell['uuid']})
   
    res = testapp.get(library_url['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent barcode details'
               for error in errors_list)