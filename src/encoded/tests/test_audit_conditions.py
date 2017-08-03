def test_rfa(award, biosample, root):
    from ..audit.conditions import rfa
    rfa_condition = rfa(award['rfa'])
    context = root.get_by_uuid(biosample['uuid'])
    system = {
        "context": context,
        "root": root,
    }
    assert rfa_condition(biosample, system)

def test_rfa_file_failure(award, file, root):
    from ..audit.conditions import rfa
    rfa_condition = rfa('GGR', 'Roadmap')
    context = root.get_by_uuid(file['uuid'])
    system = {
        "context": context,
        "root": root,
    }
    assert rfa_condition(file, system) is False