from snovault import upgrade_step


@upgrade_step('antibody_characterization', '11', '12')
def antibody_characterization(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3848
    for characterization_review in value.get('characterization_reviews'):
        if characterization_review.get('biosample_type') == 'immortalized cell line':
            characterization_review['biosample_type'] = "cell line"
