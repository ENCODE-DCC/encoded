from snovault import upgrade_step


@upgrade_step('target', '', '2')
def target_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('target', '2', '3')
def target_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1424

    tag_targets = [
        'eGFP',
        '3XFLAG',
        'HA',
        'YFP',
        'FLAG'
    ]

    nucleotide_targets = [
        'Methylcytidine'
    ]

    other_targets = [
        'H3',
        'H4'
    ]

    ambiguous_targets = [
        'POLR2AphosphoS2',
        'POLR2AphosphoS5'
    ]

    control_targets = [
        'Control',
        'goat-IgG-control',
        'mouse-IgG-control',
        'rabbit-IgG-control',
        'rat-IgG-control',
        'T7-control',
        'Input library control',
        'No protein target control',
        'Non-specific target control'
    ]

    recombinant_targets = [
        'HA',
        'YFP',
        '3XFLAG',
        'eGFP'
    ]

    histone_targets = [
        'H2AK5ac',
        'H2AK9ac',
        'H2BK120ac',
        'H2BK12ac',
        'H2BK15ac',
        'H2BK20ac',
        'H2BK5ac',
        'H2Bub',
        'H3K14ac',
        'H3K18ac',
        'H3K23ac',
        'H3K23me2',
        'H3K27ac',
        'H3K27me1',
        'H3K27me2',
        'H3K27me3',
        'H3K36ac',
        'H3K36me1',
        'H3K36me2',
        'H3K36me3',
        'H3K4ac',
        'H3K4me1',
        'H3K4me2',
        'H3K4me3',
        'H3K56ac',
        'H3K79me1',
        'H3K79me2',
        'H3K79me3',
        'H3K9ac',
        'H3K9acS10ph',
        'H3K9me1',
        'H3K9me2',
        'H3K9me3',
        'H3S10ph',
        'H3T11ph',
        'H3ac',
        'H4K12ac',
        'H4K16ac',
        'H4K20me1',
        'H4K5ac',
        'H4K8ac',
        'H4K91ac',
        'H4ac'
    ]

    tag_prefix = value['label'].split('-')[0]

    if value['label'] in tag_targets:
        value['investigated_as'] = ['tag']
    elif value['label'] in nucleotide_targets:
        value['investigated_as'] = ['nucleotide modification']
    elif value['label'] in other_targets:
        value['investigated_as'] = ['other context']
    elif value['label'] in ambiguous_targets:
        value['investigated_as'] = ['other context', 'transcription factor']
    elif value['label'] in control_targets:
        value['investigated_as'] = ['control']
    elif tag_prefix in recombinant_targets:
        value['investigated_as'] = [
            'recombinant protein', 'transcription factor']
    elif value['label'] in histone_targets:
        value['investigated_as'] = ['histone modification']
    else:
        value['investigated_as'] = ['transcription factor']


@upgrade_step('target', '3', '4')
def target_3_4(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'dbxref' in value:
        value['dbxref'] = list(set(value['dbxref']))

    if 'investigated_as' in value:
        value['investigated_as'] = list(set(value['investigated_as']))


@upgrade_step('target', '5', '6')
def target_5_6(value, system):
    if value['status'] == 'proposed':
        value['status'] = 'current'


@upgrade_step('target', '6', '7')
def target_6_7(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3981
    if 'histone modification' in value['investigated_as']:
        value['investigated_as'].remove('histone modification')


@upgrade_step('target', '7', '8')
def target_7_8(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3871
    status = value['status']
    if status == 'current':
        value['status'] = 'released'
    # Shouldn't be any of these.
    elif status == 'replaced':
        value['status'] = 'deleted'
