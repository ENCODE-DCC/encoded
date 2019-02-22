from snovault import upgrade_step
from .shared import ENCODE2_AWARDS, REFERENCES_UUID
from pyramid.traversal import find_root
import re


@upgrade_step('antibody_characterization', '', '3')
@upgrade_step('biosample_characterization', '', '3')
def characterization_0_3(value, system):
    # http://redmine.encodedcc.org/issues/428
    new_characterization_method = {
        "western blot": "immunoblot",
        "western blot after IP": "immunoprecipitation",
        "Western blot, Western blot after IP": "immunoprecipitation",
        "immunofluorescence": "FACs analysis",
        "knockdowns": "knockdown or knockout",
        "mass spectrometry after IP": "immunoprecipitation followed by mass spectrometry",
        "chIP comparison": "ChIP-seq comparison",
        "dot blot": "dot blot assay",
        "peptide ELISA": "peptide ELISA assay",
        "competitor peptides": "peptide competition assay",
        "mutant organisms": "mutant organism",
        "mutant histones": "mutant histone"
    }

    if 'characterization_method' in value:
        if value['characterization_method'] in new_characterization_method.keys():
            new_value = new_characterization_method[value['characterization_method']]
            value['characterization_method'] = new_value

    # http://redmine.encodedcc.org/issues/442
    new_status = {
        "UNSUBMITTED": "IN PROGRESS",
        "INCOMPLETE": "IN PROGRESS",
        "FAILED": "NOT SUBMITTED FOR REVIEW BY LAB",
        "APPROVED": "NOT REVIEWED",
        "SUBMITTED": "PENDING DCC REVIEW",
        "DELETED": "DELETED"
    }

    if 'status' in value:
        if value['status'] in new_status.keys():
            new_value = new_status[value['status']]
            value['status'] = new_value


@upgrade_step('antibody_characterization', '3', '4')
def antibody_characterization_3_4(value, system):
    # http://redmine.encodedcc.org/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('biosample_characterization', '3', '4')
def characterization_3_4(value, system):
    # http://redmine.encodedcc.org/issues/1307
    # http://redmine.encodedcc.org/issues/1295

    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'IN PROGRESS' and value['award'] in ENCODE2_AWARDS:
            value['status'] = 'released'
        elif value['status'] == 'IN PROGRESS' and value['award'] not in ENCODE2_AWARDS:
            value['status'] = 'in progress'


@upgrade_step('antibody_characterization', '4', '5')
def antibody_characterization_4_5(value, system):
    # http://redmine.encodedcc.org/issues/380
    primary = [
        "immunoblot",
        "immunoprecipitation",
        "immunofluorescence"
    ]

    secondary = [
        "knockdown or knockout",
        "immunoprecipitation followed by mass spectrometry",
        "ChIP-seq comparison",
        "motif enrichment",
        "dot blot assay",
        "peptide array assay",
        "peptide ELISA assay",
        "peptide competition assay",
        "overexpression analysis"
    ]

    if 'characterization_method' in value:
        if value['characterization_method'] in primary:
            value['primary_characterization_method'] = value['characterization_method']
        elif value['characterization_method'] in secondary:
            value['secondary_characterization_method'] = value['characterization_method']
        del value['characterization_method']

    if 'status' in value:
        if value['status'] == 'not reviewed':
            value['reviewed_by'] = 'ff7b77e7-bb55-4307-b665-814c9f1e65fb'
        elif value['status'] in ['compliant', 'not compliant']:
            value['reviewed_by'] = '81a6cc12-2847-4e2e-8f2c-f566699eb29e'
            value['documents'] = ['88dc12f7-c72d-4b43-a6cd-c6f3a9d08821']


@upgrade_step('antibody_characterization', '5', '6')
def antibody_characterization_5_6(value, system):
    # http://redmine.encodedcc.org/issues/2591
    context = system['context']
    root = find_root(context)
    publications = root['publications']
    if 'references' in value:
        new_references = []
        for ref in value['references']:
            item = publications[ref]
            new_references.append(str(item.uuid))
        value['references'] = new_references


@upgrade_step('biosample_characterization', '4', '5')
@upgrade_step('donor_characterization', '4', '5')
def characterization_4_5(value, system):
    # http://redmine.encodedcc.org/issues/2591
    context = system['context']
    root = find_root(context)
    publications = root['publications']
    if 'references' in value:
        new_references = []
        for ref in value['references']:
            if re.match('doi', ref):
                new_references.append(REFERENCES_UUID[ref])
            else:
                item = publications[ref]
                new_references.append(str(item.uuid))
        value['references'] = new_references


@upgrade_step('biosample_characterization', '5', '6')
@upgrade_step('donor_characterization', '5', '6')
def characterization_5_6(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'references' in value:
        value['references'] = list(set(value['references']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))


@upgrade_step('antibody_characterization', '6', '7')
def antibody_characterization_6_7(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'references' in value:
        value['references'] = list(set(value['references']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))


@upgrade_step('biosample_characterization', '6', '7')
@upgrade_step('donor_characterization', '6', '7')
def characterization_6_7(value, system):
    # Let's get all the characterizations objects back in sync on version numbers
    return


@upgrade_step('antibody_characterization', '7', '8')
@upgrade_step('biosample_characterization', '7', '8')
@upgrade_step('donor_characterization', '7', '8')
def characterization_7_8(value, system):
    # http://redmine.encodedcc.org/issues/1384
    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']
    if 'caption' in value:
        if value['caption']:
            value['caption'] = value['caption'].strip()
        else:
            del value['caption']
    if 'comment' in value:
        if value['comment']:
            value['comment'] = value['comment'].strip()
        else:
            del value['comment']
    if 'submitter_comment' in value:
        if value['submitter_comment']:
            value['submitter_comment'] = value['submitter_comment'].strip()
        else:
            del value['submitter_comment']


@upgrade_step('antibody_characterization', '9', '10')
def antibody_characterization_9_10(value, system):
    # http://redmine.encodedcc.org/issues/4925
    return


@upgrade_step('antibody_characterization', '10', '11')
@upgrade_step('biosample_characterization', '10', '11')
@upgrade_step('donor_characterization', '10', '11')
@upgrade_step('genetic_modification_characterization', '3', '4')
def characterization_10_11(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3584
    if 'comment' in value:
        value['submitter_comment'] = value['comment']
        del value['comment']


@upgrade_step('antibody_characterization', '11', '12')
def antibody_characterization_11_12(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3848
    characterization_reviews = value.get('characterization_reviews')
    if characterization_reviews:
        for characterization_review in characterization_reviews:
            if characterization_review.get('biosample_type') == 'immortalized cell line':
                characterization_review['biosample_type'] = "cell line"

@upgrade_step('antibody_characterization', '12', '13')
def antibody_characterization_12_13(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3974
    return


@upgrade_step('antibody_characterization', '13', '14')
def antibody_characterization_13_14(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3555
    characterization_reviews = value.get('characterization_reviews')
    if characterization_reviews:
        for characterization_review in characterization_reviews:
            if characterization_review.get('biosample_type') == 'induced pluripotent stem cell line':
                characterization_review['biosample_type'] = 'cell line'
            if characterization_review.get('biosample_type') == 'stem cell':
                if characterization_review.get('biosample_term_name') in ['MSiPS', 'E14TG2a.4', 'UCSF-4', 'HUES9', 'HUES8', 'HUES66',
                    'HUES65', 'HUES64', 'HUES63', 'HUES62', 'HUES6', 'HUES53', 'HUES49', 'HUES48', 'HUES45', 'HUES44', 'HUES3', 'HUES28',
                    'HUES13', 'ES-I3', 'ES-E14', 'CyT49', 'BG01', 'ES-CJ7', 'WW6', 'ZHBTc4-mESC', 'ES-D3', 'H7-hESC', 'ELF-1', 'TT2',
                    '46C', 'ES-Bruce4', 'HUES1', 'H9', 'H1-hESC', 'BG02', 'R1', 'G1E-ER4', 'G1E']:
                    characterization_review['biosample_type'] = 'cell line'
                elif characterization_review.get('biosample_term_name') in ['hematopoietic stem cell', 'embryonic stem cell',
                    'mammary stem cell', 'mesenchymal stem cell of the bone marrow', "mesenchymal stem cell of Wharton's jelly",
                    'mesenchymal stem cell of adipose', 'amniotic stem cell', 'stem cell of epidermis', 'mesenchymal stem cell',
                    'dedifferentiated amniotic fluid mesenchymal stem cell', 'leukemia stem cell', 'neuronal stem cell',
                    'neuroepithelial stem cell', 'neural stem progenitor cell']:
                    characterization_review['biosample_type'] = 'primary cell'


@upgrade_step('antibody_characterization', '14', '15')
def antibody_characterization_14_15(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4360
    for char_review in value.get('characterization_reviews', []):
        biosample_type_name = u'{}_{}'.format(
            char_review['biosample_type'], char_review['biosample_term_id']
        ).replace(' ', '_').replace(':', '_')
        char_review['biosample_ontology'] = str(
            find_root(system['context'])['biosample-types'][biosample_type_name].uuid
        )
