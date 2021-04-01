import operator

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


def make_inequality_from_relation_and_value(relation, value):
    return partial_inequality(
        relation_to_operator[relation],
        value
    )
