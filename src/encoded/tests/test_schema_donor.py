import pytest


def test_age_humanpostnatal(testapp, human_postnatal_donor_base):
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '9'}, status=422)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age_units': 'year'}, status=422)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '>89', 'age_units': 'year'}, status=200)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '9', 'age_units': 'year'}, status=200)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '9-15', 'age_units': 'year'}, status=200)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '6-9', 'age_units': 'year'}, status=200)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '92', 'age_units': 'year'}, status=422)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '102', 'age_units': 'year'}, status=422)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '6-', 'age_units': 'year'}, status=422)
    testapp.patch_json(human_postnatal_donor_base['@id'], {'age': '-6', 'age_units': 'year'}, status=422)
