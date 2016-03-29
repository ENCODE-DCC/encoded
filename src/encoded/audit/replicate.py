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


@audit_checker('replicate', frame=['experiment',
                                   'experiment.documents',
                                   'library'])
def audit_replicate_library_documents(value, system):
    '''
    If any of the library methods say <see document> then
    there needs to be a document.
    '''

    if value['status'] in ['deleted']:
        return
    if 'library' not in value:
        return
    library = value['library']

    list_of_methods = ['extraction_method',
                       'fragmentation_method',
                       'library_size_selection_method',
                       'lysis_method',
                       ]

    general_document_flag = False
    if 'experiment' in value and 'documents' in value['experiment']:
        for d in value['experiment']['documents']:
            if 'document_type' in d and \
               d['document_type'] == 'general protocol':
                general_document_flag = True

    for method in list_of_methods:
        if library.get(method) == "see document" and \
           library['documents'] == [] and \
           general_document_flag is not True:
            detail = 'Library {} method specifies "see document" yet has no document'.format(
                library['@id']
                )
            yield AuditFailure('missing documents', detail, level='NOT_COMPLIANT')
            return