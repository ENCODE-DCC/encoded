from functools import lru_cache

@lru_cache()
def assay_term_name(*assay_names):
    """ file.dataset.assay_term_name auditor condition factory
    """
    def assay_name_condition(value, system):
        context = system['context']
        assay_uuid = context.upgrade_properties()['dataset']
        assay_name = _assay_name(assay_uuid, system['root'])
        return assay_name in assay_names
    return assay_name_condition

@lru_cache()
def _assay_name(assay_uuid, root):
    assay = root.get_by_uuid(assay_uuid)
    return assay.upgrade_properties().get('assay_term_name')


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
