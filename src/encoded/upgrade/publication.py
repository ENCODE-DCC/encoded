from contentbase import upgrade_step


@upgrade_step('publication', '', '2')
def publication(value, system):
    # http://redmine.encodedcc.org/issues/2591
    value['identifiers'] = []

    if 'references' in value:
        for reference in value['references']:
            value['identifiers'].append(reference)
        del value['references']
    
    # http://redmine.encodedcc.org/issues/2725
    # /labs/encode-consortium/
    value['lab'] = "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    # /awards/ENCODE/
    value['award'] = "b5736134-3326-448b-a91a-894aafb77876"
