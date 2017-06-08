from snovault import upgrade_step
from .shared import ENCODE2_AWARDS


@upgrade_step('library', '', '3')
def library_0_3(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'CURRENT':
            if value['award'] in ENCODE2_AWARDS:
                value['status'] = 'released'
            elif value['award'] not in ENCODE2_AWARDS:
                value['status'] = 'in progress'


@upgrade_step('library', '3', '4')
def library_3_4(value, system):
    # http://redmine.encodedcc.org/issues/2784
    # http://redmine.encodedcc.org/issues/2560

    if 'paired_ended' in value:
        del value['paired_ended']

    covaris_generic = [
        'A combination of random priming and covaris shearing',
        'covaris sheering',
        'covarius'
        ]

    sonication_generic = [
        'probe in',
        'probe-in',
        'sonication'
    ]

    chemical_generic = [
        'magnesium-catalyzed hydrolysis',
        'chemical'
    ]

    tagmentation = [
        'Illumina/Nextera tagmentation',
        'Nextera Tagmentation'
    ]

    bioruptor_twin = [
        'biorupter twin',
        'bioruptor twin'
    ]

    if 'fragmentation_method' in value:
        if value['fragmentation_method'] in covaris_generic:
            value['fragmentation_method'] = 'shearing (Covaris generic)'
        elif value['fragmentation_method'] == 'Bioruptor 300':
            value['fragmentation_method'] = 'sonication (Bioruptor Plus)'
        elif value['fragmentation_method'] == 'Covaris S2':
            value['fragmentation_method'] = 'shearing (Covaris S2)'
        elif value['fragmentation_method'] == 'Diagenode Bioruptor':
            value['fragmentation_method'] = 'sonication (Bioruptor generic)'
        elif value['fragmentation_method'] in tagmentation:
            value['fragmentation_method'] = 'chemical (Nextera tagmentation)'
        elif value['fragmentation_method'] == 'None':
            value['fragmentation_method'] = 'none'
        elif value['fragmentation_method'] in bioruptor_twin:
            value['fragmentation_method'] = 'sonication (Bioruptor Twin)'
        elif value['fragmentation_method'] in chemical_generic:
            value['fragmentation_method'] = 'chemical (generic)'
        elif value['fragmentation_method'] == 'chemical (part of Illumina TruSeq mRNA Kit)':
            value['fragmentation_method'] = 'chemical (Illumina TruSeq)'
        elif value['fragmentation_method'] == 'not applicable':
            value['fragmentation_method'] = 'n/a'
        elif value['fragmentation_method'] in sonication_generic:
            value['fragmentation_method'] = 'sonication (generic)'
        elif value['fragmentation_method'] == 'Microtip Sonicator':
            value['fragmentation_method'] = 'sonication (generic microtip)'
        else:
            value['fragmentation_method'] = 'see document'


@upgrade_step('library', '4', '5')
def library_4_5(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'spikeins_used' in value:
        value['spikeins_used'] = list(set(value['spikeins_used']))

    if 'treatments' in value:
        value['treatments'] = list(set(value['treatments']))

    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))


@upgrade_step('library', '5', '6')
def library_5_6(value, system):
    # http://redmine.encodedcc.org/issues/2491
    if not value['depleted_in_term_name']:
        del value['depleted_in_term_name']
    if 'nucleic_acid_term_id' in value:
        del value['nucleic_acid_term_id']
    if 'depleted_in_term_id' in value:
        del value['depleted_in_term_id']
    if 'depleted_in_term_name' in value:
        value['depleted_in_term_name'] = list(set(value['depleted_in_term_name']))


@upgrade_step('library', '7', '8')
def library_7_8(value, system):
    # http://redmine.encodedcc.org/issues/5049
    return
