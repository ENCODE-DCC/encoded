from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_contributor_email(value, system):
    need_email = []
    if 'corresponding_contributors' in value:
        for user in value['corresponding_contributors']:
            if not user.get('email'):
                need_email.append(user.get('uuid'))
    if need_email:
        detail = ('Dataset {} contains corresponding_contributors {} that do not have an email.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(need_email)
            )
        )
        yield AuditFailure('no corresponding email', detail, level='ERROR')
    return


def audit_contributor_lists(value, system):
    duplicates = []
    if 'contributors' in value and 'corresponding_contributors' in value:
        for user in value['corresponding_contributors']:
            if user in value.get('contributors'):
                duplicates.append(user)
    if duplicates:
        detail = ('Dataset {} contains duplicated contributors {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(duplicates)
            )
        )
        yield AuditFailure('duplicated contributors', detail, level='ERROR')
    return


def audit_dataset_no_raw_files(value, system):
    if value['status'] not in ['released','in progress']:
        return
    raw_data = False
    if 'original_files' in value:
        for f in value['original_files']:
            if f['@type'][0] == 'RawSequenceFile' and f['no_file_available'] != True:
                raw_data = True
    if raw_data == False:
        detail = ('Dataset {} does not contain any raw sequence files.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('no raw data', detail, level='ERROR')
    return


def audit_dataset_dcp_required_properties(value, system):
    if value['status'] not in ['released','in progress']:
        return
    dcp_reqs = ['dataset_title', 'description', 'funding_organizations']
    for req in dcp_reqs:
        if req not in value:
            detail = ('Dataset {} does not have {}, required by the DCP.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    req
                )
            )
            yield AuditFailure('missing DCP-required field', detail, level='ERROR')
    dcp_optional = ['corresponding_contributors', 'contributors']
    for opt in dcp_optional:
        if opt not in value:
            detail = ('Dataset {} does not have {}, strongly encouraged by the DCP.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    opt
                )
            )
            yield AuditFailure('missing DCP-encouraged field', detail, level='ERROR')
    return


def audit_experiment_released_with_unreleased_files(value, system):
    '''
    A released experiment should not have unreleased files
    '''
    if value['status'] != 'released':
        return
    if 'original_files' not in value:
        return
    for f in value['original_files']:
        if f['status'] not in ['released', 'deleted',
                               'revoked', 'replaced',
                               'archived']:
            detail = ('Released dataset {} contains file {} that has not been released.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('mismatched file status', detail, level='INTERNAL_ACTION')
    return


function_dispatcher_with_files = {
    'audit_contributor_email': audit_contributor_email,
    'audit_contributor_lists': audit_contributor_lists,
    'audit_dataset_no_raw_files': audit_dataset_no_raw_files,
    'audit_dataset_dcp_required_properties': audit_dataset_dcp_required_properties,
    'audit_released_with_unreleased_files': audit_experiment_released_with_unreleased_files
}

@audit_checker('Dataset',
               frame=['original_files',
                    'corresponding_contributors'])
def audit_experiment(value, system):
    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system)
    return
