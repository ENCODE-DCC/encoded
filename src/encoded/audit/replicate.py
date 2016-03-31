from snovault import (
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

    if ((rep_status in ['in progress'] and exp_status in ['released',
                                                          'revoked',
                                                          'proposed',
                                                          'preliminary']) or
        (rep_status in ['released', 'revoked'] and
            exp_status not in ['released', 'revoked']) or
       (exp_status in ['deleted'] and rep_status not in ['deleted'])):
        #  If any of the three cases exist, there is an error
        detail = '{} replicate {} is in {} experiment'.format(
            rep_status,
            value['@id'],
            exp_status
            )
        raise AuditFailure('mismatched status', detail, level='DCC_ACTION')
