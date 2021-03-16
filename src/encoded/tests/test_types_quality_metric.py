import pytest

def test_idr_frip_calculation(testapp, idr_quality_metric_peak_frip):
    res = testapp.get(idr_quality_metric_peak_frip['@id'])
    assert 'frip' not in res.json

    testapp.patch_json(
        idr_quality_metric_peak_frip['@id'],
        {'Fp': 0.1, 'Nt': 10, 'F2': 0.2, 'N2': 20}
    )
    res = testapp.get(idr_quality_metric_peak_frip['@id'])
    assert 'frip' not in res.json

    testapp.patch_json(
        idr_quality_metric_peak_frip['@id'],
        {'Ft': 0.3, 'Np': 30, 'F1': 0.4, 'N1': 40}
    )
    res = testapp.get(idr_quality_metric_peak_frip['@id'])
    assert res.json['frip'] == 0.1


def test_histone_frip_calculation(testapp, histone_chipseq_quality_metric_frip):
    res = testapp.get(histone_chipseq_quality_metric_frip['@id'])
    assert 'frip' not in res.json

    testapp.patch_json(
        histone_chipseq_quality_metric_frip['@id'],
        {'Fp': 0.1, 'Ft': 10, 'F1': 0.2, 'F2': 20}
    )
    res = testapp.get(histone_chipseq_quality_metric_frip['@id'])
    assert res.json['frip'] == 20


def test_star_read_depth(testapp, bam_quality_metric_1_1):
    res = testapp.get(bam_quality_metric_1_1['@id'])
    assert res.json['read_depth'] == 1500
