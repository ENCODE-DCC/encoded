from ..migrator import upgrade_step

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
    "INCOMPLETE" : "IN PROGRESS",
    "FAILED": "NOT SUBMITTED FOR REVIEW BY LAB",
    "APPROVED": "NOT REVIEWED",
    "SUBMITTED": "PENDING DCC REVIEW"
    }
    
    if 'status' in value:
        new_value = new_status[value['status']]
        value['status'] = new_value