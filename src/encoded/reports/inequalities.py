import operator


syntax_to_operator = {
    'gt': operator.gt,
    'gte': operator.ge,
    'lt': operator.lt,
    'lte': operator.le,
}


def partial_inequality(operator, RHS):
    '''
    Used to bind the right-hand side argument to
    comparison operator for repeated use.
    '''
    def inequality(LHS):
        try:
            return operator(LHS, RHS)
        except TypeError:
            return False
    return inequality
