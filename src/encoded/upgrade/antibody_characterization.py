from snovault import upgrade_step


@upgrade_step('antibody_characterization', '9', '10')
def antibody_characterization_9_10(value, system):
    # http://redmine.encodedcc.org/issues/4925
    return
