import pytest


def test_reports_csv_csv_generator():
    from encoded.reports.csv import CSVGenerator
    csv = CSVGenerator()
    row = csv.writerow(['a', 'b', '123'])
    assert row == b'a\tb\t123\n'
