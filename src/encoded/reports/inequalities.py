import operator

from encoded.reports.serializers import map_string_to_boolean_and_int
from snosearch.interfaces import COLON


relation_to_operator = {
    'gt': operator.gt,
    'gte': operator.ge,
    'lt': operator.lt,
    'lte': operator.le,
}


def parse_inequality_param_value(value):
    return value.split(COLON, 1)


def partial_inequality(operator, right_operand):
    '''
    Used to bind the right-hand side argument to
    comparison operator for repeated use.
    '''
    def inequality(left_operand):
        return operator(left_operand, right_operand)
    return inequality


def make_inequality_from_relation_and_right_operand(relation, right_operand):
    return partial_inequality(
        relation_to_operator[relation],
        right_operand
    )


def map_param_values_to_inequalities(values):
    inequalities = []
    for value in values:
        relation, right_operand = parse_inequality_param_value(value)
        inequalities.append(
            make_inequality_from_relation_and_right_operand(
                relation,
                map_string_to_boolean_and_int(right_operand)
            )
        )
    return inequalities


def try_to_evaluate_inequality(inequality, left_operand):
    try:
        return inequality(left_operand)
    except TypeError:
        return False
