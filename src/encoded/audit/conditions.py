import functools


def memoize(obj):
    # Replace with functools.lru_cache() for Python 3.2+
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer


@memoize
def rfa(*rfa_names):
    """ award.rfa auditor condition factory
    """
    def rfa_condition(value, system):
        context = system['context']
        award_uuid = context.upgrade_properties()['award']
        rfa = _award_rfa(award_uuid, system['root'])
        return rfa in rfa_names

    return rfa_condition


@memoize
def _award_rfa(award_uuid, root):
    award = root.get_by_uuid(award_uuid)
    return award.upgrade_properties()['rfa']
