import pytest


def test_reports_inequalties_syntax_to_operator():
    from encoded.reports.inequalities import syntax_to_operator
    import operator
    assert syntax_to_operator['gt'].__name__ == 'gt'
    assert syntax_to_operator['gte'].__name__ == 'ge'
    assert syntax_to_operator['lt'].__name__ == 'lt'
    assert syntax_to_operator['lte'].__name__ == 'le'


def test_reports_inequalties_partial_inequality():
    from encoded.reports.inequalities import partial_inequality
    from encoded.reports.inequalities import syntax_to_operator
    operator = syntax_to_operator['gt']
    gt_3000 = partial_inequality(operator, 3000)
    assert not gt_3000(200)
    assert not gt_3000(3000)
    assert gt_3000(3001)
    assert gt_3000(3001.1)
    assert gt_3000(200000)
    operator = syntax_to_operator['gte']
    gte_3000 = partial_inequality(operator, 3000)
    assert gte_3000(3000)
    assert gte_3000(3001)
    assert not gte_3000(2999)
    operator = syntax_to_operator['lt']
    lt_ENCSR001 = partial_inequality(operator, 'ENCSR001')
    assert lt_ENCSR001('ENCSR000')
    assert not lt_ENCSR001('ENCSR002')
    operator = syntax_to_operator['lte']
    lte_26 = partial_inequality(operator, 26)
    assert lte_26(25)
    assert not lte_26('ENCSR002')
    
