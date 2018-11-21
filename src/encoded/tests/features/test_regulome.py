""" Test Regulome functions
    * Region/Regulome indexing
    * Regulome scoring
"""

import pytest
from time import sleep

pytestmark = [pytest.mark.indexing]


def test_one_region(testapp, workbook):
    # Call to /index needed if running only 'test_region_search' or 'test_one_region', else harmless
    res = testapp.post_json('/index', {'record': True})
    assert res.json['title'] == 'primary_indexer'
    assert res.json['cycle_took']
    # Call to /index_region needed always
    res = testapp.post_json('/index_region', {'record': True})
    assert res.json['cycle_took']
    assert res.json['title'] == 'region_indexer'
    # assert res.json['indexed'] > 0  # will be 0 if running all test
    sleep(5)  # For some reason testing fails without some winks

    res = testapp.get('http://0.0.0.0:6543/region-search/?region=chr9%3A136033506-136133506&genome=GRCh37')
    assert res.json['title'] == 'Region search'
    assert res.json['notification'] == 'Success'
    assert res.json['coordinates'] == 'chr9:136033506-136133506'
    assert len(res.json['@graph']) == 1
    assert res.json['@graph'][0]['accession'] == 'ENCSR000DZQ'
    assert len(res.json['@graph'][0]['files']) == 3
    expected = [
        'http://0.0.0.0:6543/peak_metadata/region=chr9%3A136033506-136133506&genome=GRCh37/peak_metadata.tsv',
        'http://0.0.0.0:6543/peak_metadata/region=chr9%3A136033506-136133506&genome=GRCh37/peak_metadata.json'
    ]
    assert res.json['download_elements'] == expected
    expected = {
        'hg19': {
            'Quick View': '/search/?type=File&assembly=hg19&region=chr9:136033506-136133506&dataset=/experiments/ENCSR000DZQ/&file_format=bigBed&file_format=bigWig&status=released#browser',
            'UCSC': 'http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear=http://0.0.0.0:6543/batch_hub/region%3Dchr9%253A136033506-136133506%2C%2Cgenome%3DGRCh37/hub.txt&db=hg19&position=chr9:136033306-136133706'
        }
    }
    assert res.json['visualize_batch'] == expected


def test_one_regulome(testapp, workbook):
    res = testapp.post_json('/index', {'record': True})
    assert res.json['title'] == 'primary_indexer'
    res = testapp.post_json('/index_region', {'record': True})
    assert res.json['title'] == 'region_indexer'
    sleep(5)  # For some reason testing fails without some winks

    res = testapp.get('http://0.0.0.0:6543/regulome-search/?region=rs3768324&genome=GRCh37')
    # import json
    # print(json.dumps(res.json, indent=4, sort_keys=True))
    # print(json.dumps({e['accession'] for e in res.json['@graph']}, indent=4, sort_keys=True))
    assert res.json['title'] == 'Regulome search'
    assert res.json['@type'] == ['region-search', 'Portal']
    assert res.json['notification'] == 'Success: 8 peaks in 8 files belonging to 8 datasets in this region'
    assert res.json['regulome_score'] == '1a'
    assert res.json['coordinates'] == 'chr1:39492462-39492462'
    assert {e['accession'] for e in res.json['@graph']} == {
        'ENCSR228TST', 'ENCSR061TST', 'ENCSR000DCE', 'ENCSR333TST',
        'ENCSR899TST', 'ENCSR497SKR', 'ENCSR000ENO', 'ENCSR000EVI'
    }
    expected = [
        'http://0.0.0.0:6543/regulome_download/regulome_evidence_hg19_chr1_39492462_39492462.bed',
        'http://0.0.0.0:6543/regulome_download/regulome_evidence_hg19_chr1_39492462_39492462.json'
    ]
    assert res.json['download_elements'] == expected


def test_regulome_score(testapp, workbook):
    res = testapp.post_json('/index', {'record': True})
    res = testapp.post_json('/index_region', {'record': True})
    sleep(5)  # For some reason testing fails without some winks

    res = testapp.get('http://0.0.0.0:6543/regulome-search/?region=rs3768324&genome=GRCh37')
    assert res.json['regulome_score'] == '1a'
