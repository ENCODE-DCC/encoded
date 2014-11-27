from functools import partial
_rfa_conditions = {}
_award_rfa_cache = {}


def rfa(*rfa_names):
    rfa_names = frozenset(rfa_names)
    if rfa_names not in _rfa_conditions:
        _rfa_conditions[rfa_names] = partial(_rfa, rfa_names)
    return _rfa_conditions[rfa_names]


def _rfa(rfa_names, value, system):
    context = system['context']
    award_uuid = context.upgrade_properties(finalize=False)['award']
    # Cache award rfa as these do not change
    if award_uuid not in _award_rfa_cache:
        root = system['root']
        award = root.get_by_uuid(award_uuid)
        _award_rfa_cache[award_uuid] = award.upgrade_properties(finalize=False)['rfa']
    return _award_rfa_cache[award_uuid] in rfa_names
