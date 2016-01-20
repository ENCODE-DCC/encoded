from contentbase import (
    AuditFailure,
    audit_checker,
)


@audit_checker('replicate', frame=['experiment'])
def audit_status_replicate(value, system):
    '''
    As the experiment-replicate relationship is reverse calculated, the status checker for item
    is not sufficient to catch all cases of status mismatch between replicates and experiments.
    * in-progress replicate can't have experiment in [proposed, released, deleted, revoked]
    * released or revoked replicate must be in [released or revoked]
    * if experiment is deleted, replicate must be deleted
    '''

    rep_status = value['status']
    exp_status = value['experiment']['status']

    if ((rep_status in ['in progress'] and exp_status in ['released', 'revoked', 'proposed', 'preliminary']) or
        (rep_status in ['released', 'revoked'] and exp_status not in ['released', 'revoked']) or
        (exp_status in ['deleted'] and rep_status not in ['deleted'])):
        #  If any of the three cases exist, there is an error
        detail = '{} replicate {} is in {} experiment'.format(
            rep_status,
            value['@id'],
            exp_status
            )
        raise AuditFailure('mismatched status', detail, level='DCC_ACTION')


@audit_checker('replicate', frame=['experiment', 'library', 'library.biosample'])
def audit_biosample_concordance(value, system):
    '''
    The biosample details of the experiment of a replicate and the library.biosample of a replicate
    need to match.
    '''

    if value.get('status') in ['deleted', 'replaced']:
        return

    if 'library' not in value:
        return

    if 'biosample' not in value['library']:
        return

    exp = value['experiment']['@id']
    exp_type = value['experiment'].get('biosample_type')
    exp_name = value['experiment'].get('biosample_term_name')
    exp_id = value['experiment'].get('biosample_term_id')

    bio = value['library']['biosample']['@id']
    bs_type = value['library']['biosample'].get('biosample_type')
    bs_name = value['library']['biosample'].get('biosample_term_name')
    bs_id = value['library']['biosample'].get('biosample_term_id')

    if bs_type != exp_type:
        detail = '{} has mismatched biosample_type: {}, but {} in {}'.format(
            exp,
            exp_type,
            bs_type,
            bio
            )
        yield AuditFailure('mismatched biosample_type', detail, level='ERROR')

    if bs_name != exp_name:
        detail = '{} has mismatched biosample_term_name: {}, but {} in {}'.format(
            exp,
            exp_name,
            bs_name,
            bio
            )
        yield AuditFailure('mismatched biosample_term_name', detail, level='ERROR')

    if bs_id != exp_id:
        detail = '{} has mismatched biosample_term_id: {}, but {} in {}'.format(
            bio,
            exp_id,
            bs_id,
            bio
            )
        yield AuditFailure('mismatched biosample_term_id', detail, level='ERROR')
