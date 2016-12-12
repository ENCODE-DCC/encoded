from snovault import upgrade_step


@upgrade_step('software', '', '2')
def software(value, system):
    # http://redmine.encodedcc.org/issues/2725
    # /labs/encode-consortium/
    value['lab'] = "cb0ef1f6-3bd3-4000-8636-1c5b9f7000dc"
    # /awards/ENCODE/
    value['award'] = "b5736134-3326-448b-a91a-894aafb77876"


@upgrade_step('software', '2', '3')
def software_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'software_type' in value:
        value['software_type'] = list(set(value['software_type']))

    if 'purpose' in value:
        value['purpose'] = list(set(value['purpose']))

    if 'used_by' in value:
        value['used_by'] = list(set(value['used_by']))
