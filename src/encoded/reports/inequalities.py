import operator

from encoded.reports.serializers import map_string_to_boolean_and_int
from snovault.elasticsearch.searches.interfaces import COLON


relation_to_operator = {
    'gt': operator.gt,
    'gte': operator.ge,
    'lt': operator.lt,
    'lte': operator.le,
}


def parse_inequality_param_value(value):
    return value.split(COLON, 1)


def partial_inequality(operator, RHS):
    '''
    Used to bind the right-hand side argument to
    comparison operator for repeated use.
    '''
    def inequality(LHS):
        return operator(LHS, RHS)
    return inequality


def make_inequality_from_relation_and_operand(relation, RHS):
    return partial_inequality(
        relation_to_operator[relation],
        RHS
    )


def map_param_values_to_inequalities(values):
    inequalities = []
    for value in values:
        relation, operand = parse_inequality_param_value(value)
        inequalities.append(
            make_inequality_from_relation_and_operand(
                relation,
                map_string_to_boolean_and_int(operand)
            )
        )
    return inequalities


def try_to_evaluate_inequality(inequality, LHS):
    try:
        return inequality(LHS)
    except TypeError:
        return False
