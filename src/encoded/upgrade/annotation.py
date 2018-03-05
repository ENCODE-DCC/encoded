from snovault import upgrade_step


@upgrade_step('annotation', '16', '17')
def annotation_16_17(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3848
    if value.get('biosample_type') == 'immortalized cell line':
        value['biosample_type'] = "cell line"
