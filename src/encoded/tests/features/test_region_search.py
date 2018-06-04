import pytest


def test_one_region(testapp, workbook):
    # Call to /index needed if running only 'test_region_search' or 'test_one_region', else harmless
    import time
    res = testapp.post_json('/index', {'record': True})
    assert res.json['title'] == 'primary_indexer'
    assert res.json['cycle_took']
    # Call to /index_region needed always
    res = testapp.post_json('/index_region', {'record': True})
    assert res.json['cycle_took']
    assert res.json['title'] == 'region_indexer'
    #assert res.json['indexed'] > 0  # will be 0 if running all test
    time.sleep(1)  # For some reason testing fails without some winks

    res = testapp.get('http://0.0.0.0:6543/region-search/?region=chr9%3A1-136133506&genome=GRCh37')
    assert 'Region search' in res.json['title']
    #assert 'Success: 1 peaks in 1 files belonging to 1 datasets in this region' in res.json['notification']
    assert 'Success' in res.json['notification']
    assert 'chr9:1-136133506' in res.json['coordinates']

    assert 1 == len(res.json['@graph'])
    assert 'ENCSR000DZQ' in res.json['@graph'][0]['accession']
    assert 3 == len(res.json['@graph'][0]['files'])

    expected = 'http://0.0.0.0:6543/peak_metadata/region=chr9%3A1-136133506&genome=GRCh37/peak_metadata.json'
    assert expected in res.json['download_elements']

    expected = {
        'hg19': {
            'Quick View': '/search/?type=File&assembly=hg19&region=chr9:1-136133506&dataset=/experiments/ENCSR000DZQ/&file_format=bigBed&file_format=bigWig&status=released#browser',
            'UCSC': 'http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear=http://0.0.0.0:6543/batch_hub/region%3Dchr9%253A1-136133506%2C%2Cgenome%3DGRCh37/hub.txt&db=hg19&position=chr9:-199-136133706'
        }
    }
    assert expected == res.json['visualize_batch']


def test_one_regulome(testapp, workbook):
    # Call to /index needed if running only 'test_one_regulome', else harmless
    import time
    res = testapp.post_json('/index', {'record': True})
    assert res.json['title'] == 'primary_indexer'
    # Call to /index_region needed if running only 'test_one_regulome', else harmless
    res = testapp.post_json('/index_region', {'record': True})
    assert res.json['title'] == 'region_indexer'
    #assert res.json['indexed'] > 0  # will be 0 unless runninging only 'test_one_regulome'
    time.sleep(1)  # For some reason testing fails without some winks

    res = testapp.get('http://0.0.0.0:6543/regulome-search/?region=chrX%3A107514356-107514356&genome=GRCh37')
    assert 'Regulome search' in res.json['title']

    assert 'region-search' in res.json['@type']

    # If running all tests '0 files' is expected.  If running this test alone 'No uuids' is expected.
    assert 'Success: 1 peaks in 1 files belonging to 1 datasets in this region' in res.json['notification']
    assert '5' == res.json['regulome_score']
    assert 'ENCSR000DZQ' == res.json['@graph'][0]['accession']

    expected = 'http://0.0.0.0:6543/regulome_evidence/regulomeDB_hg19_chrx_107514356_107514356.bed'
    assert expected in res.json['download_elements']


