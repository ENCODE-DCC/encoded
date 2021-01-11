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


@upgrade_step('library', '8', '9')
def library_8_9(value, system):
    if 'fragmentation_method' in value:
        value['fragmentation_methods'] = [value['fragmentation_method']]
        value.pop('fragmentation_method')


@upgrade_step('library', '9', '10')
def library_9_10(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4975
    old_to_new = {
        'ATAC buffer': 'ATAC buffer',
        'ATAC_buffer': 'ATAC buffer',
        'ATAC-seq (Greenleaf & Chang Lab protocol)': 'ATAC-seq (Greenleaf & Chang Lab protocol)',
        'Ambion mirVana <200nt fraction': 'Ambion mirVana',
        'Ambion mirVana': 'Ambion mirVana',
        'Clontech UltraLow for Illumina sequencing': 'Clontech UltraLow for Illumina sequencing',
        'C1 fluidigm': 'C1 fluidigm',
        'Maxwell 16 LEV simpleRNA Cells Kit (Promega cat#: AS1270)': 'Maxwell 16 LEV simpleRNA Cells Kit (Promega cat#: AS1270)',
        'miRNeasy Mini kit (QIAGEN cat#:217004)': 'miRNeasy Mini kit (QIAGEN cat#:217004)',
        'Possibly Trizol': 'Trizol',
        'Qaigen Kit DnEasy Blood and Tissue 69504': 'QIAGEN DNeasy Blood & Tissue Kit',
        'QIAGEN DNeasy Blood & Tissue Kit': 'QIAGEN DNeasy Blood & Tissue Kit',
        'Qiagen RNA extraction': 'Qiagen RNA extraction',
        'RIPA': 'RIPA',
        'RNeasy': 'RNeasy',
        'RNeasy Lipid Tissue Mini Kit (QIAGEN cat#74804)': 'RNeasy Lipid Tissue Mini Kit (QIAGEN cat#74804)',
        'RNeasy Plus Mini Kit Qiagen cat#74134 plus additional on column Dnase treatment': 'RNeasy Plus Mini Kit Qiagen cat#74134 plus additional on column Dnase treatment',
        'SDS': 'SDS',
        'Trizol': 'Trizol',
        'Trizol (LifeTech cat#: 15596-018)': 'Trizol',
        'Trizol (Invitrogen 15596-026)': 'Trizol',
        'TruChIP chromatin shearing reagent kit Covaris cat# 520154, sonication Covaris M220, IP (home protocol), DNA isolation with QIAquick PCR Purification Kit cat# 28104.': 'TruChIP chromatin shearing reagent kit Covaris cat# 520154, sonication Covaris M220, IP (home protocol), DNA isolation with QIAquick PCR Purification Kit cat# 28104.',
        'Zymo Quick-DNA MicroPrep (D3021)': 'Zymo Quick-DNA MicroPrep (D3021)',
        '[NPB (5% BSA (Sigma), 0.2% IGEPAL-CA630 (Sigma), cOmplete (Roche), 1mM DTT in PBS)]': '[NPB (5% BSA (Sigma), 0.2% IGEPAL-CA630 (Sigma), cOmplete (Roche), 1mM DTT in PBS)]',
        '[NPB(5%BSA(Sigma),0.2%IGEPAL-CA630(Sigma),cOmplete(Roche),1mMDTTinPBS)]': '[NPB (5% BSA (Sigma), 0.2% IGEPAL-CA630 (Sigma), cOmplete (Roche), 1mM DTT in PBS)]',
        '0.01% digitonin': '0.01% digitonin',
        '72 degrees for 3 minutes in the presence of Triton': '72 degrees for 3 minutes in the presence of Triton',
        'agarose gel extraction': 'agarose gel extraction',
        'AMPure XP bead purification': 'AMPure XP bead purification',
        'Agencourt AMPure XP': 'AMPure XP bead purification',
        'AMPUREXPbeads': 'AMPure XP bead purification',
        'dual SPRI': 'dual SPRI',
        'SPRI beads AMPURE': 'SPRI beads AMPURE',
        'SPRI beads': 'SPRI beads',
        'SPRI Beads': 'SPRI beads',
        'SPRI_beads': 'SPRI beads',
        'SPRI': 'SPRI beads',
        'Sera-mag SpeedBeads': 'Sera-mag SpeedBeads',
        'Invitrogen EGel EX 2% agarose (Cat# G402002)': 'Invitrogen EGel EX 2% agarose (Cat# G402002)',
        'eGel': 'E-Gel',
        'eGEL': 'E-Gel',
        'BluePippin': 'BluePippin',
        'BluePippin 2-10Kb': 'BluePippin 2-10Kb',
        'Pippin HT': 'Pippin HT',
        'gel followed by Amicon filters': 'gel followed by Amicon filters',
        'gel': 'gel',
        'Gel': 'gel',
        'Only RNAs greater than 200 nucleotides. The insert for the library was excised from an agarose gel': 'agarose gel extraction',
        'Only RNAs greater than 200 nucleotides. The inserts for the library will vary from ~ 100 - 700 base pairs.': 'Only RNAs greater than 200 nucleotides. The inserts for the library will vary from ~ 100 - 700 base pairs.',
        'Only RNAs greater than 200 nucleotides. The insert for the library will vary from ~ 100 - 700 base pairs.': 'Only RNAs greater than 200 nucleotides. The insert for the library will vary from ~ 100 - 700 base pairs.'
    }
    if 'extraction_method' in value:
        extr_method = value.get('extraction_method')
        extr_method = extr_method.rstrip()
        if extr_method in ['n/a', '0', 'see document', 'None', 'Diagenode Bioruptor, 20-40 cycles of 0.5 minute on and 0.5 minute off']:
            value.pop('extraction_method')
        elif extr_method in old_to_new:
            value['extraction_method'] = old_to_new[extr_method]
        else:
            if 'notes' in value:
                value['notes'] += "\t" + value['extraction_method']
            else:
                value['notes'] = value['extraction_method']
            value['extraction_method'] = 'other'

    if 'lysis_method' in value:
        lys_method = value.get('lysis_method')
        lys_method = lys_method.rstrip()
        if lys_method == 'see document':
            value.pop('lysis_method')
        elif lys_method in old_to_new:
            value['lysis_method'] = old_to_new[lys_method]
            if 'extraction_method' in value:
                if value['lysis_method'] == value['extraction_method'] and lys_method != 'SDS':
                    value.pop('lysis_method')
        else:
            if 'notes' in value:
                value['notes'] += '\t' + value['lysis_method']
            else:
                value['notes'] = lys_method
            value['lysis_method'] = 'other'

    if 'library_size_selection_method' in value:
        size_method = value.get('library_size_selection_method')
        size_method = size_method.rstrip()
        if size_method in ['none', 'see document', 'DNA', 'No size selections were done on this sample', 'no post-PCR size selection']:
            value.pop('library_size_selection_method')
        elif size_method in old_to_new:
            value['library_size_selection_method'] = old_to_new[size_method]
        else:
            if 'notes' in value:
                value['notes'] += "\t" + value['library_size_selection_method']
            else:
                value['notes'] = value['library_size_selection_method']
            value['library_size_selection_method'] = 'other'


@upgrade_step('library', '10', '11')
def library_10_11(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5080
    if 'strand_specificity' in value:
        if value['strand_specificity'] == False:
            value.pop('strand_specificity')
        elif value['strand_specificity'] == True:
            value['strand_specificity'] = 'strand-specific'


@upgrade_step('library', '11', '12')
def library_11_12(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5321
    if 'fragmentation_methods' in value:
        frag_methods = value.get('fragmentation_methods')
        if 'chemical (HindIII/DpnII restriction)' in frag_methods:
            frag_methods.remove('chemical (HindIII/DpnII restriction)')
            if 'chemical (DpnII restriction)' not in frag_methods:
                frag_methods.append('chemical (DpnII restriction)')
            if 'chemical (HindIII restriction)' not in frag_methods:
                frag_methods.append('chemical (HindIII restriction)')
            value['fragmentation_methods'] = frag_methods


@upgrade_step('library', '12', '13')
def library_12_13(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5297
    if 'adapters' in value:
        for adapter in value['adapters']:
            if 'type' in adapter:
                if adapter['type'] == '5\' adapter': adapter['type'] = 'read1 5\' adapter'
                if adapter['type'] == '3\' adapter': adapter['type'] = 'read1 3\' adapter'
            else:
                adapter['type'] = 'unspecified adapter'


@upgrade_step('library', '13', '14')
def library_13_14(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5368
    notes = value.get('notes', '')
    if 'depleted_in_term_name' in value:
        if 'polyadenylated mRNA' in value['depleted_in_term_name']:
            if value['nucleic_acid_term_name'] == 'polyadenylated mRNA':
                value['nucleic_acid_term_name'] = 'RNA'
                value['notes'] = (notes + ' The nucleic_acid_term_name of this library was automatically upgraded by ENCD-5368.').strip()


@upgrade_step('library', '14', '15')
def library_14_15(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5647
    notes = value.get('notes', '')
    if 'depleted_in_term_name' in value:
        if 'polyadenylated mRNA' in value['depleted_in_term_name']:
            if value['nucleic_acid_term_name'] == 'polyadenylated mRNA':
                value['nucleic_acid_term_name'] = 'RNA'
                value['notes'] = (notes + ' The nucleic_acid_term_name of this library was automatically upgraded by ENCD-5647.').strip()
