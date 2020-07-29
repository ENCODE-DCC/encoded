import pytest
from encoded.tests.features.conftest import app, app_settings, index_workbook


@pytest.mark.indexing
def test_metadata_view(testapp, index_workbook):
    r = testapp.get('/metadata/?type=Experiment')
    assert len(r.text.split('\n')) >= 81


@pytest.mark.indexing
def test_metadata_contains_audit_values(testapp, index_workbook):
    r = testapp.get('/metadata/?type=Experiment')
    audit_values = [
        'inconsistent library biosample',
        'lacking processed data',
        'inconsistent platforms',
        'missing documents',
        'unreplicated experiment'
    ]
    for value in audit_values:
        assert (
            value in r.text,
            f'{value} not in metadata report'
        )


@pytest.mark.indexing
def test_metadata_contains_all_values(testapp, index_workbook):
    from pkg_resources import resource_filename
    r = testapp.get('/metadata/?type=Experiment')
    actual = sorted([tuple(x.split('\t')) for x in r.text.strip().split('\n')])
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_metadata.tsv')
    with open(expected_path, 'r') as f:
        expected = sorted([tuple(x.split('\t')) for x in f.readlines()])
    for i, row in enumerate(actual):
        for j, column in enumerate(row):
            # Sometimes lists are out of order.
            expected_value = tuple(sorted([x.strip() for x in expected[i][j].split(',')]))
            actual_value = tuple(sorted([x.strip() for x in column.split(',')]))
            assert (
                expected_value == actual_value,
                f'Mistmatch on row {i} column {j}. {expected_value} != {actual_value}'
            )
