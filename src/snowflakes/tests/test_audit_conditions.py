def test_rfa(award, biosample, root):
    from ..audit.conditions import rfa
    rfa_condition = rfa(award['rfa'])
    context = root.get_by_uuid(biosample['uuid'])
    system = {
        "context": context,
        "root": root,
    }
    assert rfa_condition(biosample, system)
