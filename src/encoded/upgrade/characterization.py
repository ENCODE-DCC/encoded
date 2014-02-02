from ..migrator import upgrade_step


@upgrade_step('antibody_characterization', '2', '3')
@upgrade_step('biosample_characterization', '2', '3')
@upgrade_step('rnai_characterization', '2', '3')
def characterization_2_3(value, system):
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
