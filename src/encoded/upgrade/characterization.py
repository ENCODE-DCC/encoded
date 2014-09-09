from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS


@upgrade_step('antibody_characterization', '', '3')
@upgrade_step('biosample_characterization', '', '3')
@upgrade_step('rnai_characterization', '', '3')
@upgrade_step('construct_characterization', '', '3')
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
@upgrade_step('rnai_characterization', '3', '4')
@upgrade_step('construct_characterization', '3', '4')
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
            value['reviewed_by'] = '/users/ff7b77e7-bb55-4307-b665-814c9f1e65fb/'
        elif value['status'] in ['compliant', 'not compliant']:
            value['reviewed_by'] = '/users/81a6cc12-2847-4e2e-8f2c-f566699eb29e/'
            value['docments'] = ['88dc12f7-c72d-4b43-a6cd-c6f3a9d08821']

    if 'documents' in value and value['documents'] == []:
        del value['documents']


@upgrade_step('biosample_characterization', '4', '5')
@upgrade_step('rnai_characterization', '4', '5')
@upgrade_step('construct_characterization', '4', '5')
def characterization_4_5(value, system):
     # http://redmine.encodedcc.org/issues/380

     if 'documents' in value and value['documents'] == []:
        del value['documents']
