from ..migrator import upgrade_step


@upgrade_step('antibody_approval', '', '2')
def antibody_approval_0_2(value, system):
    # http://redmine.encodedcc.org/issues/442
    new_status = {
        "UNSUBMITTED": "AWAITING LAB CHARACTERIZATION",
        "INCOMPLETE": "AWAITING LAB CHARACTERIZATION",
        "FAILED": "NOT PURSUED",
        "APPROVED": "NOT ELIGIBLE FOR NEW DATA",
        "SUBMITTED": "PENDING DCC REVIEW",
        "DELETED": "DELETED",
    }

    if 'status' in value:
        new_value = new_status[value['status']]
        value['status'] = new_value
