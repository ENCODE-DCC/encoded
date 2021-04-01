import pytest


def test_reports_inequalties_relation_to_operator():
    from encoded.reports.inequalities import relation_to_operator
    import operator
    assert relation_to_operator['gt'].__name__ == 'gt'
    assert relation_to_operator['gte'].__name__ == 'ge'
    assert relation_to_operator['lt'].__name__ == 'lt'
    assert relation_to_operator['lte'].__name__ == 'le'


def test_reports_inequalties_partial_inequality():
    from encoded.reports.inequalities import partial_inequality
    from encoded.reports.inequalities import relation_to_operator
    operator = relation_to_operator['gt']
    gt_3000 = partial_inequality(operator, 3000)
    assert not gt_3000(200)
    assert not gt_3000(3000)
    assert gt_3000(3001)
    assert gt_3000(3001.1)
    assert gt_3000(200000)
    operator = relation_to_operator['gte']
    gte_3000 = partial_inequality(operator, 3000)
    assert gte_3000(3000)
    assert gte_3000(3001)
    assert not gte_3000(2999)
    operator = relation_to_operator['lt']
    lt_ENCSR001 = partial_inequality(operator, 'ENCSR001')
    assert lt_ENCSR001('ENCSR000')
    assert not lt_ENCSR001('ENCSR002')
    operator = relation_to_operator['lte']
    lte_26 = partial_inequality(operator, 26)
    assert lte_26(25)
    with pytest.raises(TypeError):
        lte_26('ENCSR002')


def test_reports_inequalities_parse_inequality_param_value():
    from encoded.reports.inequalities import parse_inequality_param_value
    relation, operand = parse_inequality_param_value('lte:3000')
    assert relation == 'lte'
    assert operand == '3000'
    relation, operand = parse_inequality_param_value('gte:3000:300')
    assert relation == 'gte'
    assert operand == '3000:300'


def test_reports_inequalities_make_inequality_from_relation_and_operand():
    from encoded.reports.inequalities import make_inequality_from_relation_and_operand
    inequality = make_inequality_from_relation_and_operand('lt', 3000)
    assert inequality(200)
    assert not inequality(5000)


def test_reports_inequalities_map_param_values_to_inequalities():
    from encoded.reports.inequalities import map_param_values_to_inequalities
    lte_3000, gt_22, lt_ENCSR000AAB, gte_97_54, lt_true = map_param_values_to_inequalities(
        [
            'lte:3000',
            'gt:22',
            'lt:ENCSR000AAB',
            'gte:97.54',
            'lt:true',
        ]
    )
    assert lte_3000(2999)
    assert lte_3000(3000)
    assert not lte_3000(3001)
    assert gt_22(23)
    assert not gt_22(-1)
    assert lt_ENCSR000AAB('ENCSR000AAA')
    assert not lt_ENCSR000AAB('ENCSR000ABC')
    assert gte_97_54('97.54')
    assert gte_97_54('97.56')
    assert not gte_97_54('96.54')
    assert notlt_true(True)
    assert lt_true(False)


def test_reports_inequalities_try_to_evaluate_inequality():
    from encoded.reports.inequalities import map_param_values_to_inequalities
    from encoded.reports.inequalities import try_to_evaluate_inequality
    lte_3000, gt_22, lt_ENCSR000AAB, gte_97_54, lt_true = map_param_values_to_inequalities(
        [
            'lte:3000',
            'gt:22',
            'lt:ENCSR000AAB',
            'gte:97.54',
            'lt:true',
        ]
    )
    assert try_to_evaluate_inequality(
        lte_3000, 2000
    )
    assert try_to_evaluate_inequality(
        lte_3000, 3000
    )
    assert not try_to_evaluate_inequality(
        lte_3000, 3001
    )
    assert not try_to_evaluate_inequality(
        lte_3000, 'abc123'
    )
    assert try_to_evaluate_inequality(
        gt_22, 26
    )
    assert try_to_evaluate_inequality(
        gt_22, 26.0
    )
    assert try_to_evaluate_inequality(
        gt_22, 26.4
    )
    assert not try_to_evaluate_inequality(
        gt_22, 'ENCSR000AAA'
    )
    assert try_to_evaluate_inequality(
        lt_ENCSR000AAB, 'ENCSR000AAA'
    )
    assert try_to_evaluate_inequality(
        lt_true, False
    )
    assert not try_to_evaluate_inequality(
        lt_true, 'false'
    )
    assert not try_to_evaluate_inequality(
        lt_true, '000123'
    )
