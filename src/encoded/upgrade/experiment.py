from snovault import upgrade_step


@upgrade_step('experiment', '15', '16')
def experiment_15_16(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3848
    if value.get('biosample_type') == 'immortalized cell line':
        value['biosample_type'] = "cell line"
