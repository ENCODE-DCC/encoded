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
        "ELIGIBLE FOR NEW DATA": "ELIGIBLE FOR NEW DATA"
    }

    if 'status' in value:
        if value['status'] not in new_status.values():
            new_value = new_status[value['status']]
            value['status'] = new_value


@upgrade_step('antibody_approval', '2', '3')
def antibody_approval_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()
