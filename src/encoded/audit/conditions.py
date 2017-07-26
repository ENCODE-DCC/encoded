from functools import lru_cache


@lru_cache()
def rfa(*rfa_names):
    """ award.rfa auditor condition factory
    """
    def rfa_condition(value, system):
        context = system['context']
        award_uuid = context.upgrade_properties()['award']
        rfa = _award_rfa(award_uuid, system['root'])
        return rfa in rfa_names

    return rfa_condition


@lru_cache()
def _award_rfa(award_uuid, root):
    award = root.get_by_uuid(award_uuid)
    return award.upgrade_properties().get('rfa')
