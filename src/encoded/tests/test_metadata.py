def test_metadata_view(testapp, workbook):
    r = testapp.get('/metadata/?type=Experiment')
    assert len(r.text.split('\n')) >= 81


def test_metadata_contains_audit_values(testapp, workbook):
     r = testapp.get('/metadata/?type=Experiment&audit=*')
     audit_values = [
         'biological replicates with identical biosample',
         'experiment not submitted to GEO',
         'inconsistent assay_term_name',
         'inconsistent library biosample',
         'lacking processed data',
         'inconsistent platforms',
         'mismatched status',
         'missing documents',
         'unreplicated experiment'
     ]
     for value in audit_values:
         assert value in r.text


def test_metadata_contains_all_values(testapp, workbook):
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
            if expected_value != actual_value:
                print(
                    'Mistmatch on row {} column {}. {} != {}'.format(
                        i,
                        j,
                        expected_value,
                        actual_value
                    )
                )
            assert expected_value == actual_value
