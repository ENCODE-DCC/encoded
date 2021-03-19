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


@upgrade_step('software', '5', '6')
def software_5_6(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4711
    for i, p in enumerate(value.get('purpose', [])):
        if p == 'single-nuclei ATAC-seq':
            value['purpose'][i] = 'single-nucleus ATAC-seq'


@upgrade_step('software', '6', '7')
def software_6_7(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4711
    for i, p in enumerate(value.get('purpose', [])):
        if p == 'single cell isolation followed by RNA-seq':
            value['purpose'][i] = 'single-cell RNA sequencing assay'


@upgrade_step('software', '7', '8')
def software_7_8(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5787
    notes = ''
    for i, p in enumerate(value.get('purpose', [])):
        if p == 'single-nucleus RNA-seq':
            value['purpose'][i] = 'single-cell RNA sequencing assay'
            notes += 'The purpose for this software is now scRNA-seq, upgraded from snRNA-seq.'
        elif p == 'genotyping by high throughput sequencing assay':
            value['purpose'][i] = 'whole genome sequencing assay'
            notes += 'The purpose for this software is now WGS, upgraded from genotyping HTS assay.'
    if notes != '':
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. {notes}'
        else:
            value['notes'] = notes
